import lsqfit
import numpy as np 
import gvar as gv

class fitter(object):

    def __init__(self, n_states,prior, t_period,t_range,
                 nucleon_corr=None,lam_corr=None,
                 xi_corr=None,sigma_corr=None,
                 delta_corr = None,
                 piplus_corr=None, kplus_corr=None,model_type=None):

        self.n_states = n_states
        self.t_period = t_period
        self.t_range = t_range
        self.prior = prior
        # self.single_smear = single_smear
        # self.data = data #TODO this should probably override below corrs
        # self.model_info = model_info.copy()
        self.lam_corr=lam_corr
        self.sigma_corr=sigma_corr
        self.nucleon_corr=nucleon_corr
        self.xi_corr=xi_corr
        self.delta_corr = delta_corr
        self.piplus_corr = piplus_corr
        self.kplus_corr = kplus_corr

        self.fit = None
        self.model_type = model_type
        self.prior = self._make_prior(prior)
        # self.fits = {}
        # self.extrapolate = None
        # self.simultaneous = False
        # self.y = {datatag : self.data['eps_'+datatag] for datatag in self.model_info['particles']}

    # @property
    # def extrapolate(self):
    #     if self._extrapolate is None:
    #         extrapolate = self.extrapolation
    #         self._extrapolate = extrapolate
    #     return self._extrapolate

    # @property
    # def extrapolation(self):
    #     extrapolation = Proton(datatag='proton',model_info=self.model_info).extrapolate_mass(observable='sigma_pi_n')
    #     return extrapolation
    
    

    def get_fit(self):
        if self.fit is not None:
            return self.fit
        else:
            return self._make_fit()

    def get_energies(self):

        # Don't rerun the fit if it's already been made
        if self.fit is not None:
            temp_fit = self.fit
        else:
            temp_fit = self.get_fit()

        max_n_states = np.max([self.n_states[key] for key in list(self.n_states.keys())])
        output = gv.gvar(np.zeros(max_n_states))
        output[0] = temp_fit.p['E0']
        for k in range(1, max_n_states):
            output[k] = output[0] + np.sum([(temp_fit.p['dE'][j]) for j in range(k)], axis=0)
        return output

    def _make_fit(self):
        # Essentially: first we create a model (which is a subclass of MultiFitter)
        # Then we make a fitter using the models
        # Finally, we make the fit with our two sets of correlators

        models = self._make_models_simult_fit()
        data = self._make_data()
        # prior = self._make_prior(self.prior)
        fitter = lsqfit.MultiFitter(models=models)
        # print(fitter)
        fit = fitter.lsqfit(data=data, prior=self.prior)
        # print(fit)
        self.fit = fit
        return fit

    def _make_models_simult_fit(self):
        models = np.array([])
        # if self.nucleon_corr is not None & self.lam_corr is not None & self.sigma_corr is not None & self.xi_corr is not None :
        #     # if self.mutliple_smear == False:
        #     for sink in list(self.nucleon_corr.keys()):
        #         param_keys = {
        #             'proton_E0'      : 'proton_E0',
        #             'lam_E0'         : 'lam_E0',
        #             'xi_E0'          : 'xi_E0',
        #             'sigma_E0'       : 'sigma_E0',
        #             'proton_log(dE)' : 'proton_log(dE)',
        #             'proton_z'       : 'proton_z_'+sink 
        #             # 'z_PS'      : 'z_PS',
        #         }   
        #         models = np.append(models,
        #                 GMO_model(datatag="nucleon_"+sink,
        #                 t=list(range(self.t_range['proton'][0], self.t_range['proton'][1])),
        #                 param_keys=param_keys, n_states=self.n_states['proton']))
        if self.nucleon_corr is not None:
            # if self.mutliple_smear == False:
            for sink in list(self.nucleon_corr.keys()):
                param_keys = {
                    'proton_E0'      : 'proton_E0',
                    # 'E1'      : 'E1',
                    # 'E2'      : 'E2',
                    # 'E3'      : 'E3',
                    'proton_log(dE)' : 'proton_log(dE)',
                    'proton_z'      : 'proton_z_'+sink 
                    # 'z_PS'      : 'z_PS',
                }   
                models = np.append(models,
                        proton_model(datatag="nucleon_"+sink,
                        t=list(range(self.t_range['proton'][0], self.t_range['proton'][1])),
                        param_keys=param_keys, n_states=self.n_states['proton']))
        if self.lam_corr is not None:
            # if self.mutliple_smear == False:
            for sink in list(self.lam_corr.keys()):
                param_keys = {
                    'lam_E0'      : 'lam_E0',
                    # 'E1'      : 'E1',
                    # 'E2'      : 'E2',
                    # 'E3'      : 'E3',
                    'lam_log(dE)' : 'lam_log(dE)',
                    'lam_z'      : 'lam_z_'+sink 
                    # 'z_PS'      : 'z_PS',
                }   
                models = np.append(models,
                        lam_model(datatag="lam_"+sink,
                        t=list(range(self.t_range['lam'][0], self.t_range['lam'][1])),
                        param_keys=param_keys, n_states=self.n_states['lam']))
        if self.xi_corr is not None:
            # if self.mutliple_smear == False:
            for sink in list(self.xi_corr.keys()):
                param_keys = {
                    'xi_E0'      : 'xi_E0',
                    # 'E1'      : 'E1',
                    # 'E2'      : 'E2',
                    # 'E3'      : 'E3',
                    'xi_log(dE)' : 'xi_log(dE)',
                    'xi_z'      : 'xi_z_'+sink 
                    # 'z_PS'      : 'z_PS',
                }   
                models = np.append(models,
                        xi_model(datatag="xi_"+sink,
                        t=list(range(self.t_range['xi'][0], self.t_range['xi'][1])),
                        param_keys=param_keys, n_states=self.n_states['xi']))
        
        if self.sigma_corr is not None:
            # if self.mutliple_smear == False:
            for sink in list(self.sigma_corr.keys()):
                param_keys = {
                    'sigma_E0'      : 'sigma_E0',
                    # 'E1'      : 'E1',
                    # 'E2'      : 'E2',
                    # 'E3'      : 'E3',
                    'sigma_log(dE)' : 'sigma_log(dE)',
                    'sigma_z'      : 'sigma_z_'+sink 
                    # 'z_PS'      : 'z_PS',
                }   
                models = np.append(models,
                        sigma_model(datatag="sigma_"+sink,
                        t=list(range(self.t_range['sigma'][0], self.t_range['sigma'][1])),
                        param_keys=param_keys, n_states=self.n_states['sigma']))
        if self.delta_corr is not None:
            # if self.mutliple_smear == False:
            for sink in list(self.delta_corr.keys()):
                param_keys = {
                    'delta_E0'      : 'delta_E0',
                    # 'E1'      : 'E1',
                    # 'E2'      : 'E2',
                    # 'E3'      : 'E3',
                    'delta_log(dE)' : 'delta_log(dE)',
                    'delta_z'      : 'delta_z_'+sink 
                    # 'z_PS'      : 'z_PS',
                }   
                models = np.append(models,
                        delta_model(datatag="delta_"+sink,
                        t=list(range(self.t_range['delta'][0], self.t_range['delta'][1])),
                        param_keys=param_keys, n_states=self.n_states['delta']))

        if self.piplus_corr is not None:
            for sink in list(self.piplus_corr.keys()):
                param_keys = {
                    'piplus_E0' : 'piplus_E0',
                    'piplus_log(dE)' : 'piplus_log(dE)',
                    'piplus_z'      : 'piplus_z_'+sink
                }
                models = np.append(models,
                           pi_Model(datatag="piplus_"+sink,t=list(range(self.t_range['pi'][0], self.t_range['pi'][1])), t_period=self.t_period,
                           param_keys=param_keys, n_states=self.n_states['pi']))

        if self.kplus_corr is not None:
            for sink in list(self.kplus_corr.keys()):
                param_keys = {
                    'kplus_E0' : 'kplus_E0',
                    'kplus_log(dE)' : 'kplus_log(dE)',
                    'kplus_z'      : 'kplus_z_'+sink,
                }
                models = np.append(models,
                           kplus_Model(datatag="kplus_"+sink,t=list(range(self.t_range['kplus'][0], self.t_range['kplus'][1])), t_period=self.t_period,
                           param_keys=param_keys, n_states=self.n_states['kplus']))
        return models

    # data array needs to match size of t array
    def _make_data(self):
        data = {}
        if self.nucleon_corr is not None:
            for sinksrc in list(self.nucleon_corr.keys()):
                data["nucleon_"+sinksrc] = self.nucleon_corr[sinksrc][self.t_range['proton'][0]:self.t_range['proton'][1]]
        if self.lam_corr is not None:
            for sinksrc in list(self.lam_corr.keys()):
                data["lam_"+sinksrc] = self.lam_corr[sinksrc][self.t_range['lam'][0]:self.t_range['lam'][1]]
        if self.sigma_corr is not None:
            for sinksrc in list(self.sigma_corr.keys()):
                data["sigma_"+sinksrc] = self.sigma_corr[sinksrc][self.t_range['sigma'][0]:self.t_range['sigma'][1]]
        if self.delta_corr is not None:
            for sinksrc in list(self.delta_corr.keys()):
                data["delta_"+sinksrc] = self.delta_corr[sinksrc][self.t_range['delta'][0]:self.t_range['delta'][1]]
        if self.xi_corr is not None:
            for sinksrc in list(self.xi_corr.keys()):
                data["xi_"+sinksrc] = self.xi_corr[sinksrc][self.t_range['xi'][0]:self.t_range['xi'][1]]
        if self.piplus_corr is not None:
            for sinksrc in list(self.piplus_corr.keys()):
                data["piplus_"+sinksrc] = self.piplus_corr[sinksrc][self.t_range['pi'][0]:self.t_range['pi'][1]]
        if self.kplus_corr is not None:
            for sinksrc in list(self.kplus_corr.keys()):
                data["kplus_"+sinksrc] = self.kplus_corr[sinksrc][self.t_range['kplus'][0]:self.t_range['kplus'][1]]
        return data

    def _make_prior_nested(self, prior):
        # not used yet, dont think multifitter can take nested dicts as inputs without modifications #
        resized_prior = {}

        max_n_states = np.max([self.n_states[key] for key in list(self.n_states.keys())])
        gmo_list = ['sigma_p','lambda_z','proton','xi_z','delta']
        gmo_list_ = [x for x in gmo_list]
        # print(gmo_list_)
        for corr in gmo_list:
            # print(corr)
            resized_prior[corr] = {}
            for key in list(prior[corr].keys()):
                resized_prior[corr][key] = prior[corr][key][:max_n_states]

            new_prior = resized_prior.copy()
            new_prior[corr]['E0'] = resized_prior[corr]['E'][0]
            # Don't need this entry
            new_prior.pop('E', None)

        # We force the energy to be positive by using the log-normal dist of dE
        # let log(dE) ~ eta; then dE ~ e^eta
            new_prior[corr]['log(dE)'] = gv.gvar(np.zeros(len(resized_prior[corr]['E']) - 1))
            for j in range(len(new_prior[corr]['log(dE)'])):
                #excited_state_energy = p[self.mass] + np.sum([np.exp(p[self.log_dE][k]) for k in range(j-1)], axis=0)

                # Notice that I've coded this s.t.
                # the std is determined entirely by the excited state
                # dE_mean = gv.mean(resized_prior['E'][j+1] - resized_prior['E'][j])
                # dE_std = gv.sdev(resized_prior['E'][j+1])
                temp = gv.gvar(resized_prior[corr]['E'][j+1]) - gv.gvar(resized_prior[corr]['E'][j])
                temp2 = gv.gvar(resized_prior[corr]['E'][j+1])
                temp_gvar = gv.gvar(temp.mean,temp2.sdev)
                print(temp_gvar)
                new_prior[corr]['log(dE)'][j] = np.log(temp_gvar)

        return new_prior

    def _make_prior(self,prior):
        resized_prior = {}

        max_n_states = np.max([self.n_states[key] for key in list(self.n_states.keys())])
        for key in list(prior.keys()):
            resized_prior[key] = prior[key][:max_n_states]

        new_prior = resized_prior.copy()
        for corr in ['sigma','lam','proton','xi',
        'delta','piplus','kplus']:

            new_prior[corr+'_E0'] = resized_prior[corr+'_E'][0]

        # Don't need this entry
            new_prior.pop(corr+'_E', None)

        # We force the energy to be positive by using the log-normal dist of dE
        # let log(dE) ~ eta; then dE ~ e^eta
            new_prior[corr+'_log(dE)'] = gv.gvar(np.zeros(len(resized_prior[corr+'_E']) - 1))
            for j in range(len(new_prior[corr+'_log(dE)'])):
                #excited_state_energy = p[self.mass] + np.sum([np.exp(p[self.log_dE][k]) for k in range(j-1)], axis=0)

                # Notice that I've coded this s.t.
                # the std is determined entirely by the excited state
                # dE_mean = gv.mean(resized_prior['E'][j+1] - resized_prior['E'][j])
                # dE_std = gv.sdev(resized_prior['E'][j+1])
                temp = gv.gvar(resized_prior[corr+'_E'][j+1]) - gv.gvar(resized_prior[corr+'_E'][j])
                temp2 = gv.gvar(resized_prior[corr+'_E'][j+1])
                temp_gvar = gv.gvar(temp.mean,temp2.sdev)
                new_prior[corr+'_log(dE)'][j] = np.log(temp_gvar)

        return new_prior
        
class proton_model(lsqfit.MultiFitterModel):
    def __init__(self, datatag, t, param_keys, n_states):
        super(proton_model, self).__init__(datatag)
        # variables for fit
        self.t = np.array(t)
        self.n_states = n_states
        # keys (strings) used to find the wf_overlap and energy in a parameter dictionary
        self.param_keys = param_keys

    def fitfcn(self, p, t=None):
        if t is None:
            t = self.t
        # z_PS = p[self.param_keys['z_PS']]
        # z_SS = p[self.param_keys['z_SS']]
        z = p[self.param_keys['proton_z']]
        # print(self.param_keys)
        E0 = p[self.param_keys['proton_E0']]
        log_dE = p[self.param_keys['proton_log(dE)']]
        # wf = 0
        output = z[0] * np.exp(-E0 * t)
        # print(output)
        for j in range(1, self.n_states):
            excited_state_energy = E0 + np.sum([np.exp(log_dE[k]) for k in range(j)], axis=0)
            output = output +z[j] * np.exp(-excited_state_energy * t)
        return output

    # The prior determines the variables that will be fit by multifitter --
    # each entry in the prior returned by this function will be fitted
    def buildprior(self, prior, mopt=None, extend=False):
        # Extract the model's parameters from prior.
        return prior

    def builddata(self, data):
        # Extract the model's fit data from data.
        # Key of data must match model's datatag!
        return data[self.datatag]

    # def fcn_effective_mass(self, p, t=None):
    #     if t is None:
    #         t=self.t
        
    #     num = 0
    #     num += self.fitfcn()

    #     return np.log(self.fitfcn(p, t) / self.fitfcn(p, t+1))

class lam_model(lsqfit.MultiFitterModel):
    def __init__(self, datatag, t, param_keys, n_states):
        super(lam_model, self).__init__(datatag)
        # variables for fit
        self.t = np.array(t)
        self.n_states = n_states
        # keys (strings) used to find the wf_overlap and energy in a parameter dictionary
        self.param_keys = param_keys

    def fitfcn(self, p, t=None):
        if t is None:
            t = self.t

        # z_PS = p[self.param_keys['z_PS']]
        # z_SS = p[self.param_keys['z_SS']]
        z = p[self.param_keys['lam_z']]
        # print(self.param_keys)
        E0 = p[self.param_keys['lam_E0']]
        log_dE = p[self.param_keys['lam_log(dE)']]
        # wf = 0
        output = z[0] * np.exp(-E0 * t)
        # print(output)
        for j in range(1, self.n_states):
            excited_state_energy = E0 + np.sum([np.exp(log_dE[k]) for k in range(j)], axis=0)
            output = output +z[j] * np.exp(-excited_state_energy * t)
        return output

    # The prior determines the variables that will be fit by multifitter --
    # each entry in the prior returned by this function will be fitted
    def buildprior(self, prior, mopt=None, extend=False):
        # Extract the model's parameters from prior.
        return prior

    def builddata(self, data):
        # Extract the model's fit data from data.
        # Key of data must match model's datatag!
        return data[self.datatag]

class xi_model(lsqfit.MultiFitterModel):
    def __init__(self, datatag, t, param_keys, n_states):
        super(xi_model, self).__init__(datatag)
        # variables for fit
        self.t = np.array(t)
        self.n_states = n_states
        # keys (strings) used to find the wf_overlap and energy in a parameter dictionary
        self.param_keys = param_keys

    def fitfcn(self, p, t=None):
        if t is None:
            t = self.t

        # z_PS = p[self.param_keys['z_PS']]
        # z_SS = p[self.param_keys['z_SS']]
        z = p[self.param_keys['xi_z']]
        # print(self.param_keys)
        E0 = p[self.param_keys['xi_E0']]
        log_dE = p[self.param_keys['xi_log(dE)']]
        # wf = 0
        output = z[0] * np.exp(-E0 * t)
        # print(output)
        for j in range(1, self.n_states):
            excited_state_energy = E0 + np.sum([np.exp(log_dE[k]) for k in range(j)], axis=0)
            output = output +z[j] * np.exp(-excited_state_energy * t)
        return output

    # The prior determines the variables that will be fit by multifitter --
    # each entry in the prior returned by this function will be fitted
    def buildprior(self, prior, mopt=None, extend=False):
        # Extract the model's parameters from prior.
        return prior

    def builddata(self, data):
        # Extract the model's fit data from data.
        # Key of data must match model's datatag!
        return data[self.datatag]

class sigma_model(lsqfit.MultiFitterModel):
    def __init__(self, datatag, t, param_keys, n_states):
        super(sigma_model, self).__init__(datatag)
        # variables for fit
        self.t = np.array(t)
        self.n_states = n_states
        # keys (strings) used to find the wf_overlap and energy in a parameter dictionary
        self.param_keys = param_keys

    def fitfcn(self, p, t=None):
        if t is None:
            t = self.t

        # z_PS = p[self.param_keys['z_PS']]
        # z_SS = p[self.param_keys['z_SS']]
        z = p[self.param_keys['sigma_z']]
        # print(self.param_keys)
        E0 = p[self.param_keys['sigma_E0']]
        log_dE = p[self.param_keys['sigma_log(dE)']]
        # wf = 0
        output = z[0] * np.exp(-E0 * t)
        # print(output)
        for j in range(1, self.n_states):
            excited_state_energy = E0 + np.sum([np.exp(log_dE[k]) for k in range(j)], axis=0)
            output = output +z[j] * np.exp(-excited_state_energy * t)
        return output

    # The prior determines the variables that will be fit by multifitter --
    # each entry in the prior returned by this function will be fitted
    def buildprior(self, prior, mopt=None, extend=False):
        # Extract the model's parameters from prior.
        return prior

    def builddata(self, data):
        # Extract the model's fit data from data.
        # Key of data must match model's datatag!
        return data[self.datatag]
class delta_model(lsqfit.MultiFitterModel):
    def __init__(self, datatag, t, param_keys, n_states):
        super(delta_model, self).__init__(datatag)
        # variables for fit
        self.t = np.array(t)
        self.n_states = n_states
        # keys (strings) used to find the wf_overlap and energy in a parameter dictionary
        self.param_keys = param_keys

    def fitfcn(self, p, t=None):
        if t is None:
            t = self.t

        # z_PS = p[self.param_keys['z_PS']]
        # z_SS = p[self.param_keys['z_SS']]
        z = p[self.param_keys['delta_z']]
        # print(self.param_keys)
        E0 = p[self.param_keys['delta_E0']]
        log_dE = p[self.param_keys['delta_log(dE)']]
        # wf = 0
        output = z[0] * np.exp(-E0 * t)
        # print(output)
        for j in range(1, self.n_states):
            excited_state_energy = E0 + np.sum([np.exp(log_dE[k]) for k in range(j)], axis=0)
            output = output +z[j] * np.exp(-excited_state_energy * t)
        return output

    # The prior determines the variables that will be fit by multifitter --
    # each entry in the prior returned by this function will be fitted
    def buildprior(self, prior, mopt=None, extend=False):
        # Extract the model's parameters from prior.
        return prior

    def builddata(self, data):
        # Extract the model's fit data from data.
        # Key of data must match model's datatag!
        return data[self.datatag]
# Used for particles that obey bose-einstein statistics
class pi_Model(lsqfit.MultiFitterModel):
    def __init__(self, datatag, t, t_period, param_keys, n_states):
        super(pi_Model, self).__init__(datatag)
        # variables for fit
        self.t = np.array(t)
        self.t_period = 64
        self.n_states = n_states

        # keys (strings) used to find the wf_overlap and energy in a parameter dictionary
        self.param_keys = param_keys


    def fitfcn(self, p, t=None):

        if t is None:
            t = self.t

        z = p[self.param_keys['piplus_z']]
        E0 = p[self.param_keys['piplus_E0']]
        dE = np.exp(p[self.param_keys['piplus_log(dE)']])
        #  r += z_snk * z_src * (np.exp(-E_n*t) + np.exp(-E_n*(T-t)))

        # r += z_snk * z_src * (np.exp(-E_n*t) + np.exp(-E_n*(T-t)))
        # return r
        output = z[0] * (np.cosh(E0 *(t-self.t_period/2)))
        for j in range(1, self.n_states):
            E_j = E0 + np.sum([dE[k] for k in range(j)], axis=0)
            output = output+ z[j] *np.cosh( E_j *(t-self.t_period/2))
        #     output = output + z[j] * np.exp( -E_j * (self.t_period-t) )

        return output

    # The prior determines the variables that will be fit by multifitter --
    # each entry in the prior returned by this function will be fitted
    def buildprior(self, prior, mopt=None, extend=False):
        return prior


    def builddata(self, data):
        # Extract the model's fit data from data.
        # Key of data must match model's datatag!
        return data[self.datatag]


    def fcn_effective_mass(self, p, t=None):
        if t is None:
            t=self.t

        return np.arccosh((self.fitfcn(p, t-1) + self.fitfcn(p, t+1))/(2*self.fitfcn(p, t)))


    def fcn_effective_wf(self, p, t=None):
        if t is None:
            t=self.t
        return 1 / np.cosh(self.fcn_effective_mass(p, t)*(t - self.t_period/2)) * self.fitfcn(p, t)

class kplus_Model(lsqfit.MultiFitterModel):
    def __init__(self, datatag, t, t_period, param_keys, n_states):
        super(kplus_Model, self).__init__(datatag)
        # variables for fit
        self.t = np.array(t)
        self.t_period = t_period
        self.n_states = n_states

        # keys (strings) used to find the wf_overlap and energy in a parameter dictionary
        self.param_keys = param_keys


    def fitfcn(self, p, t=None):

        if t is None:
            t = self.t

        z = p[self.param_keys['kplus_z']]
        E0 = p[self.param_keys['kplus_E0']]
        dE = np.exp(p[self.param_keys['kplus_log(dE)']])

        output = z[0] * (np.cosh(E0 *(t-self.t_period/2)))
        for j in range(1, self.n_states):
            E_j = E0 + np.sum([dE[k] for k in range(j)], axis=0)
            output = output+ z[j] *np.cosh( E_j *(t-self.t_period/2))
        #     output = output + z[j] * np.exp( -E_j * (self.t_period-t) )

        return output

    # The prior determines the variables that will be fit by multifitter --
    # each entry in the prior returned by this function will be fitted
    def buildprior(self, prior, mopt=None, extend=False):
        return prior


    def builddata(self, data):
        # Extract the model's fit data from data.
        # Key of data must match model's datatag!
        return data[self.datatag]


    def fcn_effective_mass(self, p, t=None):
        if t is None:
            t=self.t

        return np.arccosh((self.fitfcn(p, t-1) + self.fitfcn(p, t+1))/(2*self.fitfcn(p, t)))


    def fcn_effective_wf(self, p, t=None):
        if t is None:
            t=self.t
        return 1 / np.cosh(self.fcn_effective_mass(p, t)*(t - self.t_period/2)) * self.fitfcn(p, t)




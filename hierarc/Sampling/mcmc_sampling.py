import emcee
from hierarc.Likelihood.cosmo_likelihood import CosmoLikelihood
from lenstronomy.Util import sampling_util


class MCMCSampler(object):
    """
    class which executes the different sampling  methods
    """
    def __init__(self, kwargs_likelihood_list, cosmology, kwargs_bounds, ppn_sampling=False,
                 lambda_mst_sampling=False, lambda_mst_distribution='delta', anisotropy_sampling=False,
                 anisotropy_model='OM', custom_prior=None, interpolate_cosmo=True, num_redshift_interp=100,
                 cosmo_fixed=None):
        """
        initialise the classes of the chain and for parameter options

        :param kwargs_likelihood_list: keyword argument list specifying the arguments of the LensLikelihood class
        :param cosmology: string describing cosmological model
        :param kwargs_bounds: keyword arguments for the bounds and fixed parameters
        :param kwargs_bounds: keyword arguments of the lower and upper bounds and parameters that are held fixed.
        Includes:
        'kwargs_lower_lens', 'kwargs_upper_lens', 'kwargs_fixed_lens',
        'kwargs_lower_kin', 'kwargs_upper_kin', 'kwargs_fixed_kin'
        'kwargs_lower_cosmo', 'kwargs_upper_cosmo', 'kwargs_fixed_cosmo'
        :param ppn_sampling:post-newtonian parameter sampling
        :param lambda_mst_sampling: bool, if True adds a global mass-sheet transform parameter in the sampling
        :param lambda_mst_distribution: string, defines the distribution function of lambda_mst
        :param anisotropy_sampling: bool, if True adds a global stellar anisotropy parameter that alters the single lens
        kinematic prediction
        :param anisotropy_model: string, specifies the stellar anisotropy model
        :param custom_prior: None or a definition that takes the keywords from the CosmoParam conventions and returns a
        log likelihood value (e.g. prior)
        :param interpolate_cosmo: bool, if True, uses interpolated comoving distance in the calculation for speed-up
        :param num_redshift_interp: int, number of redshift interpolation steps
        :param cosmo_fixed: astropy.cosmology instance to be used and held fixed throughout the sampling

        """
        self.chain = CosmoLikelihood(kwargs_likelihood_list, cosmology, kwargs_bounds, ppn_sampling=ppn_sampling,
                                     lambda_mst_sampling=lambda_mst_sampling,
                                     lambda_mst_distribution=lambda_mst_distribution,
                                     anisotropy_sampling=anisotropy_sampling, anisotropy_model=anisotropy_model,
                                     custom_prior=custom_prior, interpolate_cosmo=interpolate_cosmo,
                                     num_redshift_interp=num_redshift_interp, cosmo_fixed=cosmo_fixed)
        self.param = self.chain.param

    def mcmc_emcee(self, n_walkers, n_burn, n_run, kwargs_mean_start, kwargs_sigma_start):
        """
        runs the EMCEE MCMC sampling

        :param n_walkers: number of walkers
        :param n_burn: number of iteration of burn in (not stored in the output sample
        :param n_run: number of iterations (after burn in) to be sampled
        :param kwargs_mean_start: keyword arguments of the mean starting position
        :param kwargs_sigma_start: keyword arguments of the spread in the initial particles per parameter
        :return: samples of the EMCEE run
        """

        num_param = self.param.num_param
        sampler = emcee.EnsembleSampler(n_walkers, num_param, self.chain.likelihood, args=())
        mean_start = self.param.kwargs2args(**kwargs_mean_start)
        sigma_start = self.param.kwargs2args(**kwargs_sigma_start)
        p0 = sampling_util.sample_ball(mean_start, sigma_start, n_walkers)
        sampler.run_mcmc(p0, n_burn+n_run, progress=True)
        flat_samples = sampler.get_chain(discard=n_burn, thin=1, flat=True)
        log_prob = sampler.get_log_prob(discard=n_burn, thin=1, flat=True)
        return flat_samples, log_prob

    def param_names(self, latex_style=False):
        """
        list of parameter names being sampled in the same order as teh sampling

        :param latex_style: bool, if True returns strings in latex symbols, else in the convention of the sampler
        :return: list of strings
        """
        labels = self.param.param_list(latex_style=latex_style)
        return labels

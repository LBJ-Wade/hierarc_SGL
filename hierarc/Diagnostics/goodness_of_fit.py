import matplotlib.pyplot as plt
import numpy as np
from hierarc.Likelihood.lens_sample_likelihood import LensSampleLikelihood
from lenstronomy.Util import constants as const


class GoodnessOfFit(object):
    """
    class to manage goodness of fit diagnostics
    """
    def __init__(self, kwargs_likelihood_list):
        """

        :param kwargs_likelihood_list: list of likelihood kwargs of individual lenses consistent with the
        LensLikelihood module
        """
        self._kwargs_likelihood_list = kwargs_likelihood_list
        self._sample_likelihood = LensSampleLikelihood(kwargs_likelihood_list)

    def plot_fit(self, cosmo, kwargs_lens, kwargs_kin):
        """
        plots the prediction and the uncorrelated error bars on the individual lenses
        currently works for likelihood classes 'TDKinGaussian', 'KinGaussian'

        :param cosmo: astropy.cosmology instance
        :param kwargs_lens: lens model parameter keyword arguments
        :param kwargs_kin: kinematics model keyword arguments
        :return: fig, axes of matplotlib instance
        """

        # list of values for 'KinGaussian' likelihood
        ds_dds_model_list = []
        ds_dds_name_list = []
        ds_dds_data_list = []
        ds_dds_sigma_list = []

        # list of values for 'TDKinGaussian' likelihood
        ddt_model_list = []
        ddt_name_list = []
        ddt_data_list = []
        ddt_sigma_list = []

        dd_model_list = []
        dd_name_list = []
        dd_data_list = []
        dd_sigma_list = []

        sigma_v_name_list = []
        sigma_v_measurement_list = []
        sigma_v_measurement_error_list = []
        sigma_v_model_list = []
        sigma_v_model_error_list = []

        for i, kwargs_likelihood in enumerate(self._kwargs_likelihood_list):
            name = kwargs_likelihood['name']
            likelihood = self._sample_likelihood._lens_list[i]
            ddt, dd = likelihood.angular_diameter_distances(cosmo)
            ddt_, dd_ = likelihood.displace_prediction(ddt, dd, **kwargs_lens)
            aniso_param_array = likelihood.draw_anisotropy(**kwargs_kin)
            if likelihood.likelihood_type == 'TDKinGaussian':
                dd_ = dd_ * likelihood.ani_scaling(aniso_param_array)[0]
                ddt_model_list.append(ddt_)
                ddt_name_list.append(name)
                ddt_data_list.append(kwargs_likelihood['ddt_mean'])
                ddt_sigma_list.append(kwargs_likelihood['ddt_sigma'])

                dd_model_list.append(dd_)
                dd_name_list.append(name)
                dd_data_list.append(kwargs_likelihood['dd_mean'])
                dd_sigma_list.append(kwargs_likelihood['dd_sigma'])

            elif likelihood.likelihood_type == 'KinGaussian':
                dd_ = dd_ * likelihood.ani_scaling(aniso_param_array)[0]
                ds_dds_model_list.append(ddt_ / dd_ / (1 + likelihood._z_lens))
                ds_dds_data_list.append(kwargs_likelihood['ds_dds_mean'])
                ds_dds_sigma_list.append(kwargs_likelihood['ds_dds_sigma'])
                ds_dds_name_list.append(name)
            elif likelihood.likelihood_type == 'IFUKinCov':
                dd_ = dd_ * likelihood.ani_scaling(aniso_param_array)[0]
                ds_dds =ddt_ / dd_ / (1 + likelihood._z_lens)

                j_model = kwargs_likelihood['j_model'][0]
                J_error = kwargs_likelihood['error_cov_j_sqrt']
                sigma_v = kwargs_likelihood['sigma_v_measurement'][0]
                sigma_v_sigma = np.sqrt(kwargs_likelihood['error_cov_measurement'][0, 0])
                sigma_v_predict = np.sqrt(j_model) * const.c * np.sqrt(ds_dds) / 1000
                #sigma_v_sigma_tot = np.sqrt(sigma_v_sigma ** 2 + const.c ** 2 * ds_dds * J_error / 1000 ** 2)
                sigma_v_sigma_model = np.sqrt(const.c ** 2 * ds_dds * J_error / 1000 ** 2)
                sigma_v_name_list.append(name)
                sigma_v_measurement_list.append(sigma_v)
                sigma_v_measurement_error_list.append(sigma_v_sigma)
                sigma_v_model_list.append(sigma_v_predict)
                sigma_v_model_error_list.append(sigma_v_sigma_model)

        f, axes = plt.subplots(1, 3, figsize=(12, 4))
        axes[0].errorbar(np.arange(len(ddt_name_list)), ddt_data_list, yerr=ddt_sigma_list, xerr=None, fmt='o', ecolor=None, elinewidth=None,
                     capsize=None, barsabove=False, lolims=False, uplims=False,
                     xlolims=False, xuplims=False, errorevery=1, capthick=None, data=None)
        axes[0].plot(np.arange(len(ddt_name_list)), ddt_model_list, 'ok')
        axes[0].set_xticks(ticks=np.arange(len(ddt_name_list)))
        axes[0].set_xticklabels(labels=ddt_name_list, rotation='vertical')
        axes[0].set_ylabel(r'$D_{\Delta t}$ [Mpc]', fontsize=15)

        axes[1].errorbar(np.arange(len(dd_name_list)), dd_data_list, yerr=dd_sigma_list, xerr=None, fmt='o',
                         ecolor=None, elinewidth=None,
                         capsize=None, barsabove=False, lolims=False, uplims=False,
                         xlolims=False, xuplims=False, errorevery=1, capthick=None, data=None)
        axes[1].plot(np.arange(len(dd_name_list)), dd_model_list, 'ok')
        axes[1].set_xticks(ticks=np.arange(len(dd_name_list)))
        axes[1].set_xticklabels(labels=dd_name_list, rotation='vertical')
        axes[1].set_ylabel(r'$D_{\rm d}$ [Mpc]', fontsize=15)

        axes[2].errorbar(np.arange(len(sigma_v_name_list)), sigma_v_measurement_list,
                         yerr=sigma_v_measurement_error_list, xerr=None, fmt='o',
                         ecolor=None, elinewidth=None,
                         capsize=None, barsabove=False, lolims=False, uplims=False,
                         xlolims=False, xuplims=False, errorevery=1, capthick=None, data=None, label='measurement')
        axes[2].errorbar(np.arange(len(sigma_v_name_list)), sigma_v_model_list,
                         yerr=sigma_v_model_error_list, xerr=None, fmt='o',
                         ecolor=None, elinewidth=None, label='prediction')
        axes[2].plot(np.arange(len(ds_dds_name_list)), ds_dds_model_list, 'ok')
        axes[2].set_xticks(ticks=np.arange(len(sigma_v_name_list)))
        axes[2].set_xticklabels(labels=sigma_v_name_list, rotation='vertical')
        axes[2].set_ylabel(r'$\sigma^{\rm P}$ [km/s]', fontsize=15)
        axes[2].legend()

        #axes[3].errorbar(np.arange(len(ds_dds_name_list)), ds_dds_data_list, yerr=ds_dds_sigma_list, xerr=None, fmt='o',
        #                 ecolor=None, elinewidth=None,
        #                 capsize=None, barsabove=False, lolims=False, uplims=False,
        #                 xlolims=False, xuplims=False, errorevery=1, capthick=None, data=None)
        #axes[3].plot(np.arange(len(ds_dds_name_list)), ds_dds_model_list, 'ok')
        #axes[3].set_xticks(ticks=np.arange(len(ds_dds_name_list)))
        #axes[3].set_xticklabels(labels=ds_dds_name_list, rotation='vertical')
        #axes[3].set_ylabel(r'$D_{\rm s}/D_{\rm ds}$', fontize=15)

        # separate panel for
        # IFU fit
        return f, axes

    def plot_ifu_fit(self, ax, cosmo, kwargs_lens, kwargs_kin, lens_index, show_legend=True):
        """
        plot an individual IFU data goodness of fit

        :param ax: matplotlib axes instance
        :param cosmo: astropy.cosmology instance
        :param kwargs_lens: lens model parameter keyword arguments
        :param kwargs_kin: kinematics model keyword arguments
        :param lens_index: int, index in kwargs_lens to be plotted (needs to by of type 'IFUKinCov')
        :param show_legend: bool, to show legend
        :return: figure as axes instance
        """
        kwargs_likelihood = self._kwargs_likelihood_list[lens_index]
        name = kwargs_likelihood['name']
        likelihood = self._sample_likelihood._lens_list[lens_index]
        if not likelihood.likelihood_type == 'IFUKinCov':
            raise ValueError('likelihood type of lens %s is %s. Must be "IFUKinCov"' %(name, likelihood.likelihood_type))
        ddt, dd = likelihood.angular_diameter_distances(cosmo)
        ddt_, dd_ = likelihood.displace_prediction(ddt, dd, **kwargs_lens)
        aniso_param_array = likelihood.draw_anisotropy(**kwargs_kin)
        aniso_scaling = likelihood.ani_scaling(aniso_param_array)
        ifu_likelihood = likelihood._lens_type
        ds_dds = ddt_ / dd_ / (1 + likelihood._z_lens)
        sigma_v_model = ifu_likelihood.sigma_v_model(ds_dds, aniso_scaling=aniso_scaling)
        cov_error_model = ifu_likelihood.cov_error_model(ds_dds, scaling_ifu=aniso_scaling)

        sigma_v_data = ifu_likelihood._sigma_v_measured
        cov_error_data = ifu_likelihood._error_cov_measurement

        ax.errorbar(np.arange(len(sigma_v_data)), sigma_v_data, yerr=np.sqrt(np.diag(cov_error_data)), xerr=None,
                      fmt='o', label='data')
        ax.errorbar(np.arange(len(sigma_v_model)), sigma_v_model, yerr=np.sqrt(np.diag(cov_error_model)), xerr=None,
                      fmt='o', label='model')
        if show_legend is True:
            ax.legend(fontsize=20)
        ax.set_title(name, fontsize=20)
        ax.set_ylabel(r'$\sigma^{\rm P}$[km/s]', fontsize=20)
        return ax

import pytest
from hierarc.Likelihood.transformed_cosmography import TransformedCosmography


class TestTransformedCoismography(object):

    def setup(self):
        z_lens = 0.5
        z_source = 1.5
        self.transform = TransformedCosmography(z_lens=z_lens, z_source=z_source)

    def test_displace_prediction(self):

        ddt, dd, ds = 1, 1, 1
        amp_source = 1
        # case where nothing happens
        ddt_, dd_, amp_source_ = self.transform.displace_prediction(ddt, dd, ds, gamma_ppn=1, lambda_mst=1, kappa_ext=0,
                                                                    amp_source=amp_source)
        assert ddt == ddt_
        assert dd == dd_
        assert amp_source_ == amp_source

        # case where kappa_ext is displaced
        kappa_ext = 0.1
        ddt_, dd_, amp_source_ = self.transform.displace_prediction(ddt, dd, ds, gamma_ppn=1, lambda_mst=1,
                                                                    kappa_ext=kappa_ext, amp_source=amp_source)
        assert ddt_ == ddt * (1 - kappa_ext)
        assert dd_ == dd
        assert amp_source_ == amp_source / (1 - kappa_ext)**2

        # case where lambda_mst is displaced
        lambda_mst = 0.9
        ddt_, dd_, amp_source_ = self.transform.displace_prediction(ddt, dd, ds, gamma_ppn=1, lambda_mst=lambda_mst,
                                                                    kappa_ext=0, amp_source=amp_source)
        assert ddt_ == ddt * lambda_mst
        assert dd == dd_
        assert amp_source_ == amp_source / lambda_mst ** 2

        # case for gamma_ppn
        gamma_ppn = 1.1
        ddt_, dd_, amp_source_ = self.transform.displace_prediction(ddt, dd, ds, gamma_ppn=gamma_ppn, lambda_mst=1,
                                                                    kappa_ext=0, amp_source=amp_source)
        assert ddt_ == ddt
        assert dd_ == dd * (1 + gamma_ppn) / 2.
        assert amp_source_ == amp_source

    def test_displace_kappa_ext(self):
        ddt, dd = 1, 1
        kappa_ext = 0.1
        ddt_, dd_ = self.transform._displace_kappa_ext(ddt, dd, kappa_ext=kappa_ext)
        assert ddt_ == ddt * (1 - kappa_ext)
        assert dd == dd_


if __name__ == '__main__':
    pytest.main()

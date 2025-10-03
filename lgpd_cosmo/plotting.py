
import numpy as np
import matplotlib.pyplot as plt

def plot_cls(ell, cls_base, cls_mod, out_png):
    plt.figure()
    if 'TT' in cls_base:
        Dl0 = ell*(ell+1)*cls_base['TT']/(2*np.pi)
        Dl1 = ell*(ell+1)*cls_mod['TT']/(2*np.pi)
        plt.loglog(ell, Dl0, label='TT baseline')
        plt.loglog(ell, Dl1, label='TT modified')
    if 'EE' in cls_base:
        Dl0 = ell*(ell+1)*cls_base['EE']/(2*np.pi)
        Dl1 = ell*(ell+1)*cls_mod['EE']/(2*np.pi)
        plt.loglog(ell, Dl0, label='EE baseline')
        plt.loglog(ell, Dl1, label='EE modified')
    if 'TE' in cls_base:
        Dl0 = np.abs(ell*(ell+1)*cls_base['TE']/(2*np.pi))
        Dl1 = np.abs(ell*(ell+1)*cls_mod['TE']/(2*np.pi))
        plt.loglog(ell, Dl0, label='TE |baseline|')
        plt.loglog(ell, Dl1, label='TE |modified|')
    plt.xlabel(r'$\ell$')
    plt.ylabel(r'$D_\ell$')
    plt.legend()
    plt.savefig(out_png, bbox_inches='tight')
    plt.close()

def plot_gamma(a, gamma, out_png):
    plt.figure()
    plt.loglog(a, gamma)
    plt.xlabel('a')
    plt.ylabel('Gamma(a) [s^-1] (arb.)')
    plt.savefig(out_png, bbox_inches='tight')
    plt.close()

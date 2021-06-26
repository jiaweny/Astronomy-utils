import numpy as np
import matplotlib.pyplot as plt


def region_around_line(w, flux, cont):
    """[Cut out and normalize flux around a line]

    Args:
        w ([np.array]): [array of wavelength]
        flux ([np.array]): [array of flux]
        cont ([list of lists]): [lists of wavelength
        range for continuum normalization [[low1,up1],[low2, up2]]
        that describes two areas on both sides of the line.
        This is used to fit a straight line for normalization.]

    Returns:
        [dict]: [keys: 
                wl: list, wavelengths of cut out region,
                fl: list, normalized flux of cutout region,
                endpoints: list of lists with shape (2,2),
                        [[x1,y1], [x2,y2]]

    """

    w = np.array(w)
    flux = np.array(flux)
    # index is true in the region where we fit the polynomial
    indcont = ((w > cont[0][0]) & (w < cont[0][1])) | (
        (w > cont[1][0]) & (w < cont[1][1]))
    # index of the region we want to return
    indrange = (w > cont[0][0]) & (w < cont[1][1])
    # make a flux array of shape
    # (number of spectra, number of points in indrange)
    f = np.zeros(len(flux))
    # fit polynomial of second order to the continuum region
    linecoeff = np.polyfit(w[indcont], flux[indcont], 1)

    # divide the flux by the polynomial and put the result in our
    # new flux array
    f = flux[indrange] / np.polyval(linecoeff, w[indrange])
    rst = {'wl': w[indrange], 'fl': f, 'endpoints': [
        [cont[0][0], np.polyval(linecoeff, cont[0][0])], [cont[1][1], np.polyval(linecoeff, cont[1][1])]]}
    return rst

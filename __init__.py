from .ffp_tools import FfpToolsPlugin

def classFactory(iface):
    return FfpToolsPlugin(iface)
"Functions that convert CLI args to a keyword dict for a subcommand"

from math import inf

from wildcat.utils import log


def preprocess(args):

    # Option to disable dNBR constraint
    if args.dnbr_no_adjust:
        args.dnbr_range = [-inf, inf]

    # Options to disable EVT masks
    if args.no_water:
        args.water = []
    if args.no_developed:
        args.developed = []

    # Build the keyword dict
    return {
        "input_folder": args.in_folder,
        "perimeter": args.perimeter,
        "dem": args.dem,
        "dnbr": args.dnbr,
        "kf_factor": args.kf_factor,
        "severity": args.severity,
        "evt": args.evt,
        "buffer": args.buffer,
        "dnbr_min": args.dnbr_range[0],
        "dnbr_max": args.dnbr_range[1],
        "constrain_kf": not args.kf_no_adjust,
        "kf_nodata": args.kf_nodata,
        "water": args.water,
        "developed": args.developed,
        "save": True,
        "output_folder": args.out_folder,
        "verbosity": log.verbosity(args.quiet, args.verbose),
    }

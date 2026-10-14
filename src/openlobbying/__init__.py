# muckrake overlays this repo's FtM schema extensions (Donation, Gift, ...) onto
# the followthemoney model at import time, so it must be imported before
# anything loads the model.
import muckrake  # noqa: F401

ACTOR_SCHEMATA = {"LegalEntity", "Person", "Organization", "Company", "PublicBody"}

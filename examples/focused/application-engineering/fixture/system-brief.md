# System brief

An authenticated merchant API exposes 120 units of a limited product to multiple sales channels. A client may reserve 1–5 units for ten minutes and later confirm or release the reservation. Clients retry requests after timeouts. The service must not oversell, must keep merchants isolated, and must explain whether a failed request is safe to retry. Expected peak demand is 150 reservation attempts per second during a launch.

YNCA
====

Automation Library for Yamaha receivers that support the YNCA protocol.


Installation
============

.. code-block:: bash

    pip3 install ynca


Usage
=====

This package contains:

``YncaReceiver``
    a class that represents YNCA capable receiver and allows you to control it
``ynca_console``
    a function that provides a console to directly give YNCA commands and see the responses (debugging)

Example
=======

.. code-block:: python

    # Create a receiver object. This call takes a while (multiple seconds) since
    # it communicates quite a lot with the actual device.
    # Note that later calls that control the receiver are are fast (they get async responses)
    receiver = ynca.YncaReceiver("/dev/tty1")  # Port could also be e.g. COM3 on Windows or 192.168.1.12 for IP connection

    # Attributes that are still None after initialization are not supported by the receiver/zone
    # ``receiver.zones`` is a dictionary with all available zone object for the receiver
    main = receiver.zones["MAIN"]  # other possible zones are ZONE2, ZONE3 and ZONE4
    print(main.name)  # Print the name of the main zone

    # ``receiver.inputs`` is a dictionary of available inputs with the key being
    # the unique ID and the value the friendly name if available
    print(main.inputs)

    # To get notifications when something changes register callbacks
    def on_update_callback():
        pass
    main.on_update_callback = on_update_callback

    # Examples to control the zone
    main.on = True
    main.input = "HDMI3"
    main.volume_up()

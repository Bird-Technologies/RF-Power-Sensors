from series_7027_7037 import Series_7027
import time

mysensor = Series_7027()
mysensor.connect("USB0::0x1422::0x7037::202100121::INSTR", 20000)

for k in range(10):
    print(f"Loop {k+1}")
    time.sleep(0.5)
    TMO = 0.00
    for j in range(10):
        print(mysensor.sense.frequency.frequency)
        time.sleep(TMO)
        mysensor.sense.frequency.frequency = 2.0
        time.sleep(TMO)
        print(mysensor.sense.frequency.frequency)
        time.sleep(TMO)
        mysensor.sense.frequency.frequency = 0.4
        time.sleep(TMO)
        print(mysensor._model)
        time.sleep(TMO)
        print(mysensor.sense.frequency.range_lower)
        print(mysensor.sense.frequency.range_upper)
        print(mysensor.sense.frequency.auto)

mysensor.disconnect()
time.sleep(0.5)

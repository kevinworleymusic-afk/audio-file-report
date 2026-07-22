function [output] = bandStop(input,lowFreq,highFreq)

order = 1000; 

%Low Pass Filter creation
LPF = fir1(order,lowFreq,'low');

a = conv(input,LPF);

%High Pass Filter creation
HPF = fir1(order,highFreq,'high');

b = conv(input,HPF);

output = a + b;  
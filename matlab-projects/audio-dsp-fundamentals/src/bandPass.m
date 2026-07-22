function [output] = bandPass(input,lowFreq,highFreq)
 
order = 1000; 

%Low Pass Filter creation
LPF = fir1(order,highFreq,'low');

a = conv(input,LPF);

%High Pass Filter creation
HPF = fir1(order,lowFreq,'high');

output = conv(a,HPF);




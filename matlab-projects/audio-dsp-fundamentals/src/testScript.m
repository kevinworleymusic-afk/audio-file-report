% filterTest.m

% This is a script to be used for testing your 
% filter functions

% Experiment with different length signals
x = [1;zeros(1023,1)]; % frequency in Hz

% Experiment with different coefficients
b = [1 -1];
a = [1];

% Compare the results
 y1 = filter(b,a,x);
y2 = freqFilter(b,a,x);

freqz(y2); 

%Script runs through but the final numbers don't make sense
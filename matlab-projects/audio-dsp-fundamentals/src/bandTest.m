%bandTest.m
%Kevin Worley
%

clear; clc; close all; 

[input,Fs] = audioread('AcGtr.wav'); 
% Fs = 48000; 
% input = [1 ; zeros(Fs,1)]; 
Nyq = Fs / 2; 
lowFreqHz = 1000; 
highFreqHz = 20000;

% plot(input);

lowFreq = lowFreqHz/Nyq; 
highFreq = highFreqHz/Nyq;

[output] = bandPass(input,lowFreq,highFreq);

freqz(output);

% sound(input,Fs);
sound(output,Fs)

% [output] = bandStop(input,lowFreq,highFreq); 
% freqz(output); 
% sound(output,Fs); 
 
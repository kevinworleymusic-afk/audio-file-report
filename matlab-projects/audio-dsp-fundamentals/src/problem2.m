%problem2.mf
%Kevin Worley
%

clear; clc; close all; 

%%
%Audio File Listening Example 
% [input,Fs] = audioread('AcGtr.wav'); % sound(input,Fs);  %Command to hear
% input file to make sure it works.

%Impulse
Fs = 48000;   %Setting Sample Rate 
input = [1 ; zeros(Fs,1)]; %Impulse Signal Generation
Nyq = Fs / 2;  %Calculating Nyquist frequency based off Impulse.n

%Frequency ranges
lowFreqHz = 100;  %Setting a "low" frequency band to customize
highFreqHz = 1000; %Setting a "high" frequency band to customize

%Normalizing to value between 0-1 using Nyquist
lowFreq = lowFreqHz/Nyq;   
highFreq = highFreqHz/Nyq;

% 
%Band Pass filter Code
[output] = bandPass(input,lowFreq,highFreq); %Function 
freqz(output);    %Getting graph using freqz function. 
sound(output,Fs)  %Sound Function to Test with Audio Files

%%
%Band Stop Filter Code
[output] = bandStop(input,lowFreq,highFreq); %Function
freqz(output);  %Getting graph using freqz function. 
sound(output,Fs); %Sound Function to Test with Audio Files.

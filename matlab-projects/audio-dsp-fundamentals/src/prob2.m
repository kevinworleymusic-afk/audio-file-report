%prob2.m
%Kevin Worley
%

clear; clc; close all; 

%%
%Creating the white noise file
Fs = 48000;  %Setting Sample Rate
Nyq = Fs/2;  %Setting Nyquist frequency based on FS
sec = 5;  %Duration 5 seconds
numSam = Fs * sec; %Converting seconds to num of Samples
noise = 0.2 * randn(numSam,1);  %Generating White Noise

%%
N = 16;  %Setting # of times 
order = 100; %Setting order value for FIR command
freqBin = zeros(N,1);  %Pre-allocating freq array
ampBin = zeros(N,1);   %Pre-allocating amp array

freq = 1/Nyq; %Setting Starting frequency at 1Hz-normalized to value 0-1. 
for n = 1:N     
        amp = (1/freq)/Nyq; %amp = 1/f; 
        %Normalizing to values between 0-1 dividing by Nyq
        
        %Setting an if condition to make loop max out at nyq frequency
         if freq > 1
            freq = 1; 
         end 

        freqBin(n,1) = freq;  %Indexing sample into freq array
        ampBin(n,1) = amp;    %Indexing sample into amp array
        freq = 2*freq; %Setting a new freq value for next passing of loop. 
end 

realFreqBin = [0 ; freqBin];%Adding a zero bin at the front to work with FIR
realAmpBin = [1; ampBin]; %Adding a 1 bin at the front to work with FIR 2. 
output = fir2(order, realFreqBin, realAmpBin);%Running FIR2 to generate filter. 

pink = conv(noise,output);  %Convoluting filter onto white noise signal
pinkGain = pink * 2; %Added gain change of x2 to make signal louder/more audible

%%
%Plot log frequency, dB Amp
[H,W] = freqz(pink,1,2048,Fs); %H = amp & phase,  W = array of frequencies 
%Amplitude plot 
subplot(2,1,1);   
semilogx(W,20*log10(abs(H))); axis([20 20000 -12 12]);
% subplot(2,1,2);
% % % plot(W,angle(H) * 180/pi); % match MATLAB
% semilogx(W,angle(H) * 180/pi); axis([20 20000 -90 0]);

%%
%Saving audio file
% audiowrite('pinkNoise.wav',pink,Fs); 

audiowrite('pinkNoise.wav',pinkGain,Fs);  
%Using gain boosted signal for better wav file (clip gaining it).   
%Problem3HW.m
%
%

clear; clc; close all; 

[x,Fs] = audioread('acGtr.wav'); 

g1 = .45;
g2 = -.5;
g3 = .05;

%Dry Signal Path
a = x(n,1) * g1; 

%Delay Buffer 1
fir1()


%
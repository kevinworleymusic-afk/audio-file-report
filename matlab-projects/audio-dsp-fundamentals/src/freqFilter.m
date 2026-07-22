%freqFilter.m
%
%

function [y] = freqFilter(b,a,x)

% b = array of feedforward coefficients
% a = array of feedback coefficients 
% x = input signal 
% y = output signal 

N = length(x); 
B = length(b); 
A = length(a); 

%Converting Input from time to frequency domain
X = fft(x); 

%Initializing k array; 

k = [(1:N-1),1]';


%Creating variables for H(X) Transfer
dnum = [(1:B),1]-1; 
dden = [(1:A),1]-1; 

% Hnum = b * exp(-j*2*pi*k*dnum*1/N);  
% 
% Hden = a * exp(-j*2*pi*k*dden*1/N);

 
%Preallocating Hnum and Hden arrays.
Hnum = zeros(B,1);
Hden = zeros(A,1); 

for p = 1:B

    Hnum(1,p) = b(1,p) * exp(-1i*2*pi*dnum(1,p) *(1/N));
end 

for q = 1:A

    Hden(1,q) = a(1,q) * exp(-1i*2*pi*dden(1,q)*(1/N)); 
end 

%Flipping arrays to be column vectors
Hnum = Hnum'; 
Hden = Hden';

%Summing the terms to reach length N
Hnum = sum(Hnum).* exp(k); 
Hden = sum(Hden).* exp(k);

%Solving for Transfer Function using numerator and denominator variables.  
Hk = Hnum./Hden; 

%Element wise mulitiplication to get y in frequency domain
Y = Hk .* X; 

%Getting y output in time domain. 
y = real(ifft(Y)); 

end 










clear all;

% parameters 
global alphaM alphaP epsilon rho ksiN0 ksiN1 ksiE0 ksiE1 zetaN zetaE sigma etaN etaE 

alphaM     = 0.5;   % remove alphaM
alphaP     = 0.5;   % remove alphaP 
epsilon    = 1.5;   % Humber (2023) Krusell et. al (2000)
rho        = 2.27;  % Ngai & Petrongolo (2017)
zetaN      = 0.5;   % remove zetaN
zetaE      = 0.5;   % remove zetaE
sigma      = 1.5;   % Humber (2023) Krusell et. al (2000)
etaN       = 1;     % 郭凯明和颜色（2015）郭凯明等（2021）
etaE       = 0.5;   % 郭凯明和颜色（2015）郭凯明等（2021）


% technologies
BM         = 1;
BP         = 1;
AN         = 1;
AE         = 1;
kappaN     = 1;
chi        = 0.25;  % Goldin (1990)

% state variables
N          = 1;
e          = 1;

% calibration targets
omega      = 0.75;    % W0/W1, wage gender gap
lNratio    = 3.118;   % lN0/lN1 全国时间利用调查
lEratio    = 2;       % lE0/lE1 全国时间利用调查
lratio     = 2/3;     % labor supply, female/male, (1-lN0-lE0)/(1-lN1-lE1) 人口普查 经济普查
n_base     = 0.65;    % fertility rate, 1.3, 人口普查
% calibrated parameters
ksiN0      = ((omega^rho*lNratio)^(-1)+1)^(-1); % target: lNratio
ksiN1      = 1 - ksiN0;
ksiE0      = ((omega^rho*lEratio)^(-1)+1)^(-1); % target: lEratio
ksiE1      = 1 - ksiE0;


% equilibrium
X0         = [0.75 1 0.1 0.5 1];  % guess [femaleWage maleWage e_bar betaM kappaE]

options = optimset('Display','iter', 'MaxFunEvals', 100000, 'MaxIter', 100000, 'TolFun', 1e-6, 'TolX', 1e-12);
[X,residuals,flag] = fsolve('equilibriumCalib', X0, options, BM, BP, AN, AE, kappaN, chi, N, e, omega, lratio, n_base);

W0          = X(1);
W1          = X(2);
e_bar       = X(3);
betaM       = X(4);
kappaE      = X(5);
betaP       = 1 - betaM;
WN_tilde    = (ksiN0*W0^(1-rho) + ksiN1*W1^(1-rho))^(1/(1-rho));
WE_tilde    = (ksiE0*W0^(1-rho) + ksiE1*W1^(1-rho))^(1/(1-rho));
pN          = ((1-zetaN)*AN^(sigma-1) + zetaN*kappaN^(sigma-1)*WN_tilde^(1-sigma))^(1/(1-sigma));
pE          = ((1-zetaE)*AE^(sigma-1) + zetaE*kappaE^(sigma-1)*WE_tilde^(1-sigma))^(1/(1-sigma));
n           = (etaN-etaE)/(1+etaN) * (W0+W1)/(pN-pE*e_bar);
e_prime     = etaE/(etaN-etaE)*pN/pE - etaN/(etaN-etaE)*e_bar;
WNlN_tilde  = zetaN*kappaN^(sigma-1)*WN_tilde^(1-sigma) / (zetaN*kappaN^(sigma-1)*WN_tilde^(1-sigma) + (1-zetaN)*AN^(sigma-1))*pN*n;
WElE_tilde  = zetaE*kappaE^(sigma-1)*WE_tilde^(1-sigma) / (zetaE*kappaE^(sigma-1)*WE_tilde^(1-sigma) + (1-zetaE)*AE^(sigma-1))*pE*e_prime*n;
lN0         = WNlN_tilde * ksiN0*W0^(1-rho)/WN_tilde^(1-rho) /W0;
lN1         = WNlN_tilde * ksiN1*W1^(1-rho)/WN_tilde^(1-rho) /W1;
lE0         = WElE_tilde * ksiE0*W0^(1-rho)/WE_tilde^(1-rho) /W0;
lE1         = WElE_tilde * ksiE1*W1^(1-rho)/WE_tilde^(1-rho) /W1;
LM          = ((1-lN0-lE0)+(1-lN1-lE1))*e*N;
LP          = ((1-lN0-lE0)*chi+(1-lN1-lE1))*N;
wM          = (1/(1-chi)*W0 - chi/(1-chi)*W1)/e;
wP          = (W1 - W0)/(1-chi);
PM_tilde    = ((1-alphaM)*BM^(epsilon-1) + alphaM*wM^(1-epsilon))^(1/(1-epsilon));
PP_tilde    = ((1-alphaP)*BP^(epsilon-1) + alphaP*wP^(1-epsilon))^(1/(1-epsilon));

save calib e_bar betaM kappaE;




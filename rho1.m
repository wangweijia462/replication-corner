clear all;

% parameters 
global alphaM alphaP epsilon rho ksiN0 ksiN1 ksiE0 ksiE1 zetaN zetaE sigma etaN etaE e_bar betaM betaP
load calib;         % load e_bar betaM kappaE
betaP      = 1 - betaM;
alphaM     = 0.5;   % remove alphaM
alphaP     = 0.5;   % remove alphaP 
epsilon    = 1.5;   % Humber (2023) Krusell et. al (2000)
rho        = 2.27;  % Ngai & Petrongolo (2017)
zetaN      = 0.5;   % remove zetaN
zetaE      = 0.5;   % remove zetaE
sigma      = 1.5;   % Humber (2023) Krusell et. al (2000)
etaN       = 1;     % 郭凯明和颜色（2015）郭凯明等（2021）
etaE       = 0.5;   % 郭凯明和颜色（2015）郭凯明等（2021）

% calibration targets
omega      = 0.75;    % W0/W1, wage gender gap，王美艳（2005）李实等（2014）罗楚亮等（2019）
lNratio    = 3.118;   % lN0/lN1 全国时间利用调查
lEratio    = 2;       % lE0/lE1 全国时间利用调查
lratio     = 2/3;     % labor supply, female/male, (1-lN0-lE0)/(1-lN1-lE1) 人口普查 经济普查

% calibrated parameters
ksiN0      = ((omega^rho*lNratio)^(-1)+1)^(-1); % target: lNratio
ksiN1      = 1 - ksiN0;
ksiE0      = ((omega^rho*lEratio)^(-1)+1)^(-1); % target: lEratio
ksiE1      = 1 - ksiE0;

% sensitivity
rho        = 1.5;   

% technologies
BM         = 1;
BP         = 1;
AN         = 1;
AE         = 1;
kappaN     = 1;  % kappaE calibrated
chi        = 0.25;  % Goldin (1990)

% state variables
N          = 1;
e          = 1;
T          = 11;

% changes in BM
BM_vector               = linspace(1,2,T); 
n_vector_BM             = ones(1,T);
e_prime_vector_BM       = ones(1,T);
omega_vector_BM         = ones(1,T);
L0_vector_BM            = ones(1,T);
L1_vector_BM            = ones(1,T);
W_vector_BM             = ones(1,T);
for i = 1 : T
    BM = BM_vector(i);
% equilibrium
    X0       = [1 2];  % guess [femaleWage maleWage]  
    options = optimset('Display','iter', 'MaxFunEvals', 100000, 'MaxIter', 100000, 'TolFun', 1e-6, 'TolX', 1e-12);
    [X,residuals,flag] = fsolve('equilibrium', X0, options, BM, BP, AN, AE, kappaN, kappaE, chi, N, e);

    W0       = X(1);
    W1       = X(2);
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

    n_vector_BM(i)             = n;
    e_prime_vector_BM(i)       = e_prime;
    omega_vector_BM(i)         = W0/W1;
    L0_vector_BM(i)            = 1-lN0-lE0;
    L1_vector_BM(i)            = 1-lN1-lE1;
    W_vector_BM(i)             = (1-lN0-lE0)*W0+(1-lN1-lE1)*W1;
end
BM         = 1;
% end, changes in BM

% changes in BP
BP_vector               = linspace(1,2,T); 
n_vector_BP             = ones(1,T);
e_prime_vector_BP       = ones(1,T);
omega_vector_BP         = ones(1,T);
L0_vector_BP            = ones(1,T);
L1_vector_BP            = ones(1,T);
W_vector_BP             = ones(1,T);
for i = 1 : T
    BP = BP_vector(i);
% equilibrium
    X0       = [1 2];  % guess [femaleWage maleWage]  
    options = optimset('Display','iter', 'MaxFunEvals', 100000, 'MaxIter', 100000, 'TolFun', 1e-6, 'TolX', 1e-12);
    [X,residuals,flag] = fsolve('equilibrium', X0, options, BM, BP, AN, AE, kappaN, kappaE, chi, N, e);

    W0       = X(1);
    W1       = X(2);
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

    n_vector_BP(i)             = n;
    e_prime_vector_BP(i)       = e_prime;
    omega_vector_BP(i)         = W0/W1;
    L0_vector_BP(i)            = 1-lN0-lE0;
    L1_vector_BP(i)            = 1-lN1-lE1;
    W_vector_BP(i)             = (1-lN0-lE0)*W0+(1-lN1-lE1)*W1;
end
BP         = 1;
% end, changes in BP

% changes in AN
AN_vector               = linspace(1,2,T); 
n_vector_AN             = ones(1,T);
e_prime_vector_AN       = ones(1,T);
omega_vector_AN         = ones(1,T);
L0_vector_AN            = ones(1,T);
L1_vector_AN            = ones(1,T);
W_vector_AN             = ones(1,T);
for i = 1 : T
    AN = AN_vector(i);
% equilibrium
    X0       = [1 2];  % guess [femaleWage maleWage]  
    options = optimset('Display','iter', 'MaxFunEvals', 100000, 'MaxIter', 100000, 'TolFun', 1e-6, 'TolX', 1e-12);
    [X,residuals,flag] = fsolve('equilibrium', X0, options, BM, BP, AN, AE, kappaN, kappaE, chi, N, e);

    W0       = X(1);
    W1       = X(2);
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

    n_vector_AN(i)             = n;
    e_prime_vector_AN(i)       = e_prime;
    omega_vector_AN(i)         = W0/W1;
    L0_vector_AN(i)            = 1-lN0-lE0;
    L1_vector_AN(i)            = 1-lN1-lE1;
    W_vector_AN(i)             = (1-lN0-lE0)*W0+(1-lN1-lE1)*W1;
end
AN         = 1;
% end, changes in AN

% changes in AE
AE_vector               = linspace(1,2,T); 
n_vector_AE             = ones(1,T);
e_prime_vector_AE       = ones(1,T);
omega_vector_AE         = ones(1,T);
L0_vector_AE            = ones(1,T);
L1_vector_AE            = ones(1,T);
W_vector_AE             = ones(1,T);
for i = 1 : T
    AE = AE_vector(i);
% equilibrium
    X0       = [1 2];  % guess [femaleWage maleWage]  
    options = optimset('Display','iter', 'MaxFunEvals', 100000, 'MaxIter', 100000, 'TolFun', 1e-6, 'TolX', 1e-12);
    [X,residuals,flag] = fsolve('equilibrium', X0, options, BM, BP, AN, AE, kappaN, kappaE, chi, N, e);

    W0       = X(1);
    W1       = X(2);
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

    n_vector_AE(i)             = n;
    e_prime_vector_AE(i)       = e_prime;
    omega_vector_AE(i)         = W0/W1;
    L0_vector_AE(i)            = 1-lN0-lE0;
    L1_vector_AE(i)            = 1-lN1-lE1;
    W_vector_AE(i)             = (1-lN0-lE0)*W0+(1-lN1-lE1)*W1;
end
AE         = 1;
% end, changes in AE


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% output
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
delta_n_BM       = n_vector_BM(T)-n_vector_BM(1);
delta_e_prime_BM = e_prime_vector_BM(T)-e_prime_vector_BM(1);
delta_omega_BM   = omega_vector_BM(T)-omega_vector_BM(1);
delta_W_BM       = W_vector_BM(T)-W_vector_BM(1);
delta_L0_BM      = L0_vector_BM(T)-L0_vector_BM(1);
delta_L1_BM      = L1_vector_BM(T)-L1_vector_BM(1);

delta_n_BP       = n_vector_BP(T)-n_vector_BP(1);
delta_e_prime_BP = e_prime_vector_BP(T)-e_prime_vector_BP(1);
delta_omega_BP   = omega_vector_BP(T)-omega_vector_BP(1);
delta_W_BP       = W_vector_BP(T)-W_vector_BP(1);
delta_L0_BP      = L0_vector_BP(T)-L0_vector_BP(1);
delta_L1_BP      = L1_vector_BP(T)-L1_vector_BP(1);

delta_n_AE       = n_vector_AE(T)-n_vector_AE(1);
delta_e_prime_AE = e_prime_vector_AE(T)-e_prime_vector_AE(1);
delta_omega_AE   = omega_vector_AE(T)-omega_vector_AE(1);
delta_W_AE       = W_vector_AE(T)-W_vector_AE(1);
delta_L0_AE      = L0_vector_AE(T)-L0_vector_AE(1);
delta_L1_AE      = L1_vector_AE(T)-L1_vector_AE(1);

delta_n_AN       = n_vector_AN(T)-n_vector_AN(1);
delta_e_prime_AN = e_prime_vector_AN(T)-e_prime_vector_AN(1);
delta_omega_AN   = omega_vector_AN(T)-omega_vector_AN(1);
delta_W_AN       = W_vector_AN(T)-W_vector_AN(1);
delta_L0_AN      = L0_vector_AN(T)-L0_vector_AN(1);
delta_L1_AN      = L1_vector_AN(T)-L1_vector_AN(1);

% output
delta_rho1_BM = [delta_n_BM;delta_e_prime_BM;delta_omega_BM;delta_W_BM;delta_L0_BM;delta_L1_BM]; 
delta_rho1_BP = [delta_n_BP;delta_e_prime_BP;delta_omega_BP;delta_W_BP;delta_L0_BP;delta_L1_BP]; 
delta_rho1_AE = [delta_n_AE;delta_e_prime_AE;delta_omega_AE;delta_W_AE;delta_L0_AE;delta_L1_AE]; 
delta_rho1_AN = [delta_n_AN;delta_e_prime_AN;delta_omega_AN;delta_W_AN;delta_L0_AN;delta_L1_AN]; 

save delta_rho1 delta_rho1_BM delta_rho1_BP delta_rho1_AN delta_rho1_AE ;  % rho = 1.5

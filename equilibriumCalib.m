function y = equilibriumCalib(X0, BM, BP, AN, AE, kappaN, chi, N, e, omega, lratio, n_base)

global alphaM alphaP epsilon rho ksiN0 ksiN1 ksiE0 ksiE1 zetaN zetaE sigma etaN etaE 

W0          = X0(1);
W1          = X0(2);
e_bar       = X0(3);
betaM       = X0(4);
kappaE      = X0(5);
betaP       = 1 - betaM;

% derived variables
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

% equations
y1         = (wM/wP)^epsilon - alphaM/alphaP * betaM/betaP * LP/LM * (PP_tilde/PM_tilde)^(1-epsilon);
y2         = PM_tilde^betaM*PP_tilde^betaP - 1;
y3         = (1-lN0-lE0) - (1-lN1-lE1)*lratio;
y4         = W0 - W1*omega;
y5         = n - n_base;    % 总和生育率，人口普查
y          = [y1 y2 y3 y4 y5];

end

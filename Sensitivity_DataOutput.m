clear all;

load delta_baseline.mat;

load delta_rho1.mat;
load delta_rho2.mat;
load delta_rho3.mat;
load delta_etaN1.mat;
load delta_etaN2.mat;
load delta_etaE1.mat;
load delta_etaE2.mat;
load delta_chi1.mat;
load delta_chi2.mat;
load delta_epsilon1.mat;
load delta_epsilon2.mat;
load delta_sigma1.mat;
load delta_sigma2.mat;


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% result
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
rho_Result = [delta_rho1_BM delta_rho2_BM delta_rho3_BM  ...,
    delta_rho1_BP delta_rho2_BP delta_rho3_BP  ...,
    delta_rho1_AN delta_rho2_AN delta_rho3_AN  ...,
    delta_rho1_AE delta_rho2_AE delta_rho3_AE];

etaN_Result = [delta_etaN1_BM delta_baseline_BM delta_etaN2_BM  ...,
    delta_etaN1_BP delta_baseline_BP delta_etaN2_BP  ...,
    delta_etaN1_AN delta_baseline_AN delta_etaN2_AN  ...,
    delta_etaN1_AE delta_baseline_AE delta_etaN2_AE];

etaE_Result = [delta_etaE1_BM delta_baseline_BM delta_etaE2_BM  ...,
    delta_etaE1_BP delta_baseline_BP delta_etaE2_BP  ...,
    delta_etaE1_AN delta_baseline_AN delta_etaE2_AN  ...,
    delta_etaE1_AE delta_baseline_AE delta_etaE2_AE];

chi_Result = [delta_chi1_BM delta_baseline_BM delta_chi2_BM  ...,
    delta_chi1_BP delta_baseline_BP delta_chi2_BP  ...,
    delta_chi1_AN delta_baseline_AN delta_chi2_AN  ...,
    delta_chi1_AE delta_baseline_AE delta_chi2_AE];

epsilon_Result = [delta_epsilon1_BM delta_baseline_BM delta_epsilon2_BM  ...,
    delta_epsilon1_BP delta_baseline_BP delta_epsilon2_BP  ...,
    delta_epsilon1_AN delta_baseline_AN delta_epsilon2_AN  ...,
    delta_epsilon1_AE delta_baseline_AE delta_epsilon2_AE];

sigma_Result = [delta_sigma1_BM delta_baseline_BM delta_sigma2_BM  ...,
    delta_sigma1_BP delta_baseline_BP delta_sigma2_BP  ...,
    delta_sigma1_AN delta_baseline_AN delta_sigma2_AN  ...,
    delta_sigma1_AE delta_baseline_AE delta_sigma2_AE];


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% output
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
xlswrite('SensitivityResult.xlsx',rho_Result,'rho');
xlswrite('SensitivityResult.xlsx',etaN_Result,'etaN');
xlswrite('SensitivityResult.xlsx',etaE_Result,'etaE');

xlswrite('SensitivityResult.xlsx',chi_Result,'chi');
xlswrite('SensitivityResult.xlsx',epsilon_Result,'epsilon');
xlswrite('SensitivityResult.xlsx',sigma_Result,'sigma');

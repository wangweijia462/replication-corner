clear all;

load delta_baseline.mat;
load delta_alphaS1.mat;
load delta_alphaS2.mat;
load delta_zetaD1.mat;
load delta_zetaD2.mat;

% Result
alphaS_Result = [delta_alphaS1_BM delta_baseline_BM delta_alphaS2_BM  ...,
    delta_alphaS1_BP delta_baseline_BP delta_alphaS2_BP  ...,
    delta_alphaS1_AN delta_baseline_AN delta_alphaS2_AN  ...,
    delta_alphaS1_AE delta_baseline_AE delta_alphaS2_AE];

zetaD_Result = [delta_zetaD1_BM delta_baseline_BM delta_zetaD2_BM  ...,
    delta_zetaD1_BP delta_baseline_BP delta_zetaD2_BP  ...,
    delta_zetaD1_AN delta_baseline_AN delta_zetaD2_AN  ...,
    delta_zetaD1_AE delta_baseline_AE delta_zetaD2_AE];

% output
xlswrite('DiscussionResult.xlsx',alphaS_Result,'alphaS');
xlswrite('DiscussionResult.xlsx',zetaD_Result,'zetaD');
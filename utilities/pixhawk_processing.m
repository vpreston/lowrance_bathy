L = [GPS(:,2), GPS(:,4), GPS(:,8), GPS(:,9)];
M = [ATT(:,2), ATT(:,4), ATT(:,6), ATT(:,8)];

% plot(ATT(:,4))
dlmwrite('pix_gps.csv',L,'precision',9);
dlmwrite('pix_eul.csv',M,'precision',9);
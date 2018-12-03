%% Examining Model against GroundTruth Map
% vpreston
% Dec. 3, 2018

format long g
groundtruth = readtable('ground_xyz.csv'); %data imported from QGIS software
id = (groundtruth.field_3 > -32700 & groundtruth.field_2 < max(y) & groundtruth.field_1 > min(x));

xg = groundtruth.field_1(id);
yg = groundtruth.field_2(id);
zg = groundtruth.field_3(id);
allg = [xg,yg,zg];

%% View the Ground Truth against measured data and model
figure(1)
ax1 = subplot(3,1,1);
scatter3(xg,yg,zg,1,zg)
view(2)
title('Ground Truth Measurements')
lim=caxis;
ax2 = subplot(3,1,2);
scatter3(x,y,z,1,z)
view(2)
caxis(lim)
title('Cleaned Observations')
ax3 = subplot(3,1,3);
plot(fg1)
view(2)
caxis(lim)
title('Smoothed Model')
shading interp

linkaxes([ax1,ax2,ax3],'x','y')

%% Look at the Difference Between the Models

% Project the ground truth points into the model
xfg = xg;
yfg = yg;
zfg = zg;
zf = feval(fg1,[xfg,yfg]);

% Take a look at the curves
figure
subplot(2,1,1)
scatter3(xfg, yfg, zf, 1, zf);
subplot(2,1,2)
scatter3(xfg, yfg, zfg, 1, zfg);

% Calculate the difference between the two
res = zf-zfg; %measurement - ground truth (positive residual means the groundtruth was smaller)
sse = sum(res.^2,'omitnan')
rmse = sqrt(sse/length(zf))

% Visualize the Residuals
[xfg1,id] = datasample(xfg,1000,'Replace',false);
yfg1 = yfg(id);
zfg1 = res(id);
figure
xp = [min(xfg1) max(xfg1) max(xfg1) min(xfg1)];
yp = [min(yfg1) min(yfg1) max(yfg1) max(yfg1)];
patch(xp,yp,'k','FaceAlpha',0.3)
hold on
scatter3(xfg1, yfg1, zfg1, '*')
hold on
for i=1:length(zfg1)
    lh = plot3([xfg1(i) xfg1(i)],[yfg1(i) yfg1(i)], [zfg1(i) 0],'b');
    lh.Color = [0,0,0,0.3];
end

% Count the residuals
figure
histogram(res)
xlabel('Residual (m)')
ylabel('Data Count')

%% Mean Removal Resid
res = (zf-mean(zf,'omitnan'))-(zfg-mean(zfg,'omitnan'));
sse = sum(res.^2,'omitnan')
rmse = sqrt(sse/length(zf))

%% Plot the difference surface
scatter3(xfg, yfg, res, 1, res)
colorbar
caxis([-5,1])
view(2)

%% Examining the Cleaned Data to Develop a Model
% vpreston
% Dec. 3, 2018

% Read in the file of interest
format long g
dataoffit = readtable('data_to_fit.csv');
x = dataoffit.Smoothed_X;
y = dataoffit.Smoothed_Y;
z = dataoffit.Smoothed_Z;
figure
scatter3(x,y,z,1,z)

%% Look at Slices of the Data
scatter3(x,y,z,1,z)
xlabel('Easting')
ylabel('Northing')
view(2)
figure
scatter(y,z,1,z);
xlabel('Northing');
ylabel('Depth');
figure
scatter(x,z,1,z);
xlabel('Easting');
ylabel('Depth');

%% Interpolate the Data (Linear) into a Rough Model
[fg,gofg] = fit([x, y],z,'linearinterp','Normalize','on');
figure;
plot(fg)

%% Project new points into the Rough Model

xnodes = min(x):0.1:max(x);
ynodes = min(y):0.1:max(y);
[xn,yn] = meshgrid(xnodes,ynodes);
znodes = feval(fg,[xn(:),yn(:)]);
figure
plot(fg)
shading interp

%% Smooth the projection and Get New Model
K = 1/(50*50)*ones(50);
zs = 50*conv2(znodes,K,'same');

xn = xn(~isnan(zs));
yn = yn(~isnan(zs));
zs = zs(~isnan(zs));

[fg1,gofg1] = fit([xn(:), yn(:)],zs(:),'linearinterp','Normalize','on');
figure
plot(fg1)
shading interp

%% Compare the Models and the Data
figure
ax1=subplot(3,1,1);
scatter3(x,y,z,1,z)
title('Scatter of Cleaned Data')
view(2)
lim=caxis;
ax2=subplot(3,1,2);
plot(fg)
shading interp
view(2)
caxis(lim)
title('Direct Linear Interpolation')
ax3=subplot(3,1,3);
plot(fg1)
title('Smoothed Linear Interpolation')
shading interp
view(2)
caxis(lim)

linkaxes([ax1,ax2,ax3],'x','y')

%% Look at the Model Statistics
[x1,id] = datasample(x,1000,'Replace',false);
y1 = y(id);
z1 = z(id);

figure
plot(fg1,[x1,y1],z1,'Style','Residual')
res = z1 - feval(fg1,x1,y1);
figure
histogram(res)
xlabel('Residual (m)')
ylabel('Data Count')
ops = res.^2;
sse = sum(ops,'omitnan')
rmse=sqrt(sum(ops,'omitnan')/length(res))

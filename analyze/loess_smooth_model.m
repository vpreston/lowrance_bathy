%% Examining the Data to Create a Local Quadratic Regression Model
% vpreston
% Dec. 3, 2018

% Read the data in
format long g
dataoffit = readtable('data_to_fit.csv');

x = dataoffit.Smoothed_X(1:50:end);
y = dataoffit.Smoothed_Y(1:50:end);
z = dataoffit.Smoothed_Z(1:50:end);
all = [x,y,z];

% Get a random sample of the data
[x1,id] = datasample(x,1000,'Replace',false);
y1 = y(id);
z1 = z(id);

figure
scatter3(x,y,z,1,z)

%% Perform Initial Fit by using bisquare weighting
[f,gof] = fit([x, y],z,'loess','Normalize','on');
figure;
plot(f, [x1,y1], z1)
figure;
plot(f, [x1,y1], z1,'Style','Contour')
figure;
plot(f, [x1,y1], z1,'Style','Residuals')

%% Now refit the data by ignoring outliers (can get by examining the residual plot generated above)
res = abs(z - feval(f,[x,y]));
ids = (res > 1);
outliers = excludedata(x,y,'indices',ids);

[f2,gof2] = fit([x, y],z,'loess','Normalize','on','Exclude', outliers);
figure;
plot(f2, [x1,y1], z1)
colorbar();
figure;
plot(f2, [x1,y1], z1,'Style','Contour')
figure;
plot(f2, [x1,y1], z1,'Style','Residuals')

%% Analyze the Confidence in the Fit
gof
gof2

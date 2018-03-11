import numpy as np
import matplotlib.pyplot as plt


# name of features
features = []
'''
# 25 speed quantiles
for i in list(range(25)):
	features.append("speed_quantiles_{}".format(i + 1))

# 25 accel quantiles
for i in list(range(25)):
	features.append("accel_quantiles_{}".format(i + 1))

# 10 head_quantiles_x
for i in list(range(10)):
	features.append("head_quantiles_x_{}".format(i + 1))

# 10 head_quantiles_y
for i in list(range(10)):
	features.append("head_quantiles_y_{}".format(i + 1))
'''

features.extend([
	"std_speed",
	"mean_speed",
	"var_speed",
	"std_braking",
	"mean_braking",
	"var_braking",
	"std_acceleration",
	"mean_acceleration",
	"var_acceleration",
	"std_anfahren",
	"mean_anfahren",
	"max_anfahren"
])

colors = [
	"rosybrown",
	"palegreen",
	"lightseagreen",
	"darkorange",
	"navajowhite",
	"darkturquoise",
	"darkgoldenrod",
	"sandybrown",
	"mediumaquamarine",
	"darksalmon",
	"cadetblue"
]

histo_bins = 30
trip_data = np.load("./myfeatures.npy")
print(trip_data.shape)
number_of_drivers = int(trip_data.shape[0] / 200)
number_of_features = int(trip_data.shape[1])
assert (number_of_features) == len(features)


for feature_idx, feature in enumerate(features):
	number_of_drivers = 5
	fig, axs = plt.subplots(number_of_drivers, 1)
	fig.suptitle(feature)
	feature_to_plot = [trip[feature_idx] for trip in trip_data]
	for driver_idx, driver in enumerate(list(range(number_of_drivers))):
		driver_start_idx = driver_idx * 200
		drivers_feature = feature_to_plot[driver_start_idx:driver_start_idx + 200]
		axs[driver_idx].hist(drivers_feature, histo_bins, alpha=0.5, color=colors[driver_idx])
		axs[driver_idx].set_title("driver {}".format(driver_idx))


	plt.show()

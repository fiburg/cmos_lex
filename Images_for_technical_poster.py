import matplotlib.pyplot as plt
import cmos
import numpy as np
import cv2
import sklearn.preprocessing




def save_orig_image(sky_imager,output_folder,output_name="original_image.png"):
    image = sky_imager.original_image.copy()
    image = image[:,:,::-1]
    cv2.imshow("asdf",image)
    cv2.waitKey(0)
    cv2.imwrite(output_folder+output_name, image)
    print("Saved original image at: " +output_folder + output_name )


def save_crop_mask(sky_imager,output_folder,output_name="crop_mask.png"):
    temp_image = sky_imager.original_image.copy()
    temp_image[:, :, 0] = 255
    temp_image[:, :, 1] = 255
    temp_image[:, :, 2] = 255
    image = sky_imager.crop_image(temp_image)
    image = np.asarray(image)

    image = image[:,:,::-1]
    # cv2.imshow("image",image)
    cv2.imwrite(output_folder + output_name, image)
    print("Saved crop mask at: " + output_folder + output_name)


def save_crop_image(sky_imager,output_folder,output_name="crop_image.png"):
    temp_image = sky_imager.original_image.copy()
    image = sky_imager.crop_image(temp_image)
    image = image[:,:,::-1]
    cv2.imwrite(output_folder + output_name, image)
    print("Saved cropped image at: " + output_folder + output_name)


def save_sun_mask(sky_imager,output_folder,output_name="sun_mask.png"):
    temp_image = sky_imager.original_image.copy()
    temp_image[:, :, 0] = 255
    temp_image[:, :, 1] = 255
    temp_image[:, :, 2] = 255
    temp_image = sky_imager.crop_image(temp_image)
    sun_mask = sky_imager.mask_around_sun
    temp_image[:, :, 0][sun_mask] = 0
    temp_image[:, :, 1][sun_mask] = 0
    temp_image[:, :, 2][sun_mask] = 0
    image = temp_image

    image = rotate_image(image,25)
    cv2.imwrite(output_folder + output_name, image)
    print("Saved sun mask at: " + output_folder + output_name)


def save_sun_image(sky_imager,output_folder,output_name="sun_image.png"):
    temp_image = sky_imager.image.copy()
    temp_image = rotate_image(temp_image,example_rotation)
    image = temp_image[:,:,::-1]

    cv2.imwrite(output_folder + output_name, image)
    print("Saved sun image at: " + output_folder + output_name)


def rotate_image(image, deg):
    """
    Helper function to rotate images.

    Args:
        image:
        deg:

    Returns:

    """
    rows, cols = (image.shape[0], image.shape[1])
    M = cv2.getRotationMatrix2D((cols / 2, rows / 2), -deg, 1)
    return cv2.warpAffine(image, M, (cols, rows))


def save_rotation_mask(sky_imager,output_folder,output_name="rotation_mask.png"):
    angle_image_orig = sky_imager.angle_array[:,:,0].copy()
    angle_image_offset = rotate_image(angle_image_orig,example_rotation)

    fig = plt.figure(frameon=False)
    w,h = sky_imager.get_image_size()
    fig.set_size_inches(int(w/100), int(h/100))
    ax = plt.Axes(fig, [0., 0., 1., 1.])
    ax.set_axis_off()
    fig.add_axes(ax)
    ax.imshow(angle_image_offset)
    fig.savefig(output_folder+output_name, dpi=100)
    plt.close()
    print("Saved rotation mask at: " + output_folder + output_name)

def save_rotated_image(sky_imager,output_folder,output_name="rotation_image.png"):
    temp_image = sky_imager.original_image.copy()
    temp_image = sky_imager.crop_image(temp_image)
    angle_image_offset = rotate_image(temp_image,example_rotation)
    image = angle_image_offset[:,:,::-1]
    cv2.imwrite(output_folder + output_name, image)
    print("Saved rotated image at: " + output_folder + output_name)

def save_cloud_mask(sky_imager,output_folder,output_name="cloud_mask.png"):
    cloud_mask = sky_imager.cloud_mask.copy()
    cloud_mask = rotate_image(cloud_mask, example_rotation)

    fig = plt.figure(frameon=False)
    w, h = sky_imager.get_image_size()
    fig.set_size_inches(int(w / 100), int(h / 100))
    ax = plt.Axes(fig, [0., 0., 1., 1.])
    ax.set_axis_off()
    fig.add_axes(ax)
    ax.imshow(cloud_mask)
    fig.savefig(output_folder + output_name, dpi=100)
    plt.close()
    print("Saved cloud mask at: " + output_folder + output_name)


def save_cloud_image(sky_imager,output_folder,output_name="cloud_image.png"):
    cloud_image = sky_imager.cloud_image.copy()
    cloud_image = rotate_image(cloud_image, example_rotation)

    fig = plt.figure(frameon=False)
    w, h = sky_imager.get_image_size()
    fig.set_size_inches(int(w / 100), int(h / 100))
    ax = plt.Axes(fig, [0., 0., 1., 1.])
    ax.set_axis_off()
    fig.add_axes(ax)
    ax.imshow(cloud_image)
    fig.savefig(output_folder + output_name, dpi=100)
    plt.close()
    print("Saved cloud mask at: " + output_folder + output_name)

def save_cloud_map(sky_imager,output_folder,output_name="cloud_map.png"):
    map = cmos.Map()
    fig = plt.figure(frameon=False)
    w, h = sky_imager.get_image_size()
    fig.set_size_inches(int(w / 100), int(h / 100))
    ax = plt.Axes(fig, [0., 0., 1., 1.])
    fig.add_axes(ax)
    ax = map.make_map(subplot_info=111,tile_resolution=15)
    ax.set_positional_data(date=sky_imager.date,
                            cloud_height=sky_imager.cloud_height,
                            sun_azimuth=sky_imager.sun_azimuth,
                            sun_elevation=sky_imager.sun_elevation)
    sky_imager.create_cloud_mask()
    sky_imager.create_lat_lon_cloud_mask()
    ax.create_shadow_mask(sky_imager.lat_lon_cloud_mask)
    ax.add_shadows()
    fig.savefig(output_folder + output_name, dpi=700)
    plt.close()
    print("Saved cloud map at: " + output_folder + output_name)


if __name__ == "__main__":
    output_folder = "C:/Users/darkl/Desktop/cmos/Poster/plots_for_technical_poster/"
    file = "C:/Users/darkl/Desktop/cmos/skyimager/LEX_WKM2_JPG_20180826/LEX_WKM2_Image_20180826_112520_UTCp1.jpg"
    sky_imager = cmos.SkyImager("hq")
    sky_imager.get_date_from_image_name(file)

    ceilo = cmos.Ceilometer()
    cloud_height = ceilo.get_height(sky_imager.date)
    sky_imager.load_image(file, cloud_height=cloud_height)



    # Uebtertriebene Rotation zu Veranschauungszwecken:
    global example_rotation
    example_rotation = 25

    # Diese funktionen simulieren einzeln in der richtigen Reihenfolge,
    # wie das Programm funktioniert:

    # save_orig_image(sky_imager,output_folder)
    # save_crop_mask(sky_imager,output_folder)
    # save_crop_image(sky_imager,output_folder)
    # save_rotation_mask(sky_imager,output_folder)
    save_rotated_image(sky_imager,output_folder)
    # save_sun_mask(sky_imager,output_folder)
    # save_sun_image(sky_imager,output_folder)
    # save_cloud_mask(sky_imager,output_folder)
    # save_cloud_image(sky_imager,output_folder)
    # save_cloud_map(sky_imager,output_folder)
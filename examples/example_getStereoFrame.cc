#include <UnitreeCameraSDK.hpp>
#include <unistd.h>

int main(int argc, char *argv[]){
    cv::VideoWriter writer {
        "appsrc ! videoconvert ! omxh264enc ! video/x-h264, stream-format=byte-stream ! rtph264pay ! udpsink host=192.168.123.15 port=9201",
        cv::CAP_GSTREAMER, // apiPreference
        0, // fourcc
        30, // fps
        cv::Size{928, 400}, // frameSize
        true // isColor
    };
    UnitreeCamera cam("stereo_camera_config.yaml"); ///< init UnitreeCamera object by config file
    if(!cam.isOpened())  ///< get camera open state
        exit(EXIT_FAILURE);
    
    
    cam.startCapture(); ///< disable image h264 encoding and share memory sharing

    while(cam.isOpened()){
        // std::chrono::microseconds t;

        cv::Mat left, right/*, feim*/;
        if(!cam.getRectStereoFrame(left, right/*, feim, t*/)){
            usleep(1000);
            continue;
        }
        cv::Mat stereo;
        cv::hconcat(left, right, stereo);
        cv::Mat stereo_flipped;
        cv::flip(stereo, stereo_flipped, -1);
        writer << stereo_flipped;
        
        // cv::Mat stereo;
        // if(!cam.getRawFrame(stereo, t)){
        //     usleep(1000);
        //     continue;
        // }
        // cv::Mat left, right;
        // stereo(cv::Rect(0, 0, stereo.size().width / 2, stereo.size().height)).copyTo(right);
        // stereo(cv::Rect(stereo.size().width / 2, 0, stereo.size().width / 2, stereo.size().height)).copyTo(left);
        // cv::hconcat(left, right, stereo);
        // writer << stereo;
    }

    cam.stopCapture();  ///< stop camera capturing
    writer.release();
    return 0;
}

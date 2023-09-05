/**
  * @file example_getDepthFrame.cc
  * @brief This file is part of UnitreeCameraSDK.
  * @details This example that how to get depth frame
  * @author SunMingzhe
  * @date  2021.12.07
  * @version 1.1.0
  * @copyright Copyright (c) 2020-2021, Hangzhou Yushu Technology Stock CO.LTD. All Rights Reserved.
  */

#include <UnitreeCameraSDK.hpp>
#include <unistd.h>

int main(int argc, char *argv[]){
    cv::VideoWriter writer {
        "appsrc ! videoconvert ! omxh264enc ! video/x-h264, stream-format=byte-stream ! rtph264pay ! udpsink host=192.168.123.15 port=9201",
        cv::CAP_GSTREAMER, // apiPreference
        0, // fourcc
        30, // fps
        cv::Size{464, 400}, // frameSize
        true // isColor
    };
    UnitreeCamera cam("stereo_camera_config.yaml"); ///< init UnitreeCamera object by config file
    if(!cam.isOpened())  ///< get camera open state
        exit(EXIT_FAILURE);
    
    cam.startCapture(); ///< disable image h264 encoding and share memory sharing
    cam.startStereoCompute(); ///< start disparity computing

    while(cam.isOpened()){
        cv::Mat depth; 
        std::chrono::microseconds t;
        if(!cam.getDepthFrame(depth, true, t)){  ///< get stereo camera depth image 
            usleep(1000);
            continue;
        }
        if(!depth.empty()){
            writer << depth;
        }
    }
    
    cam.stopStereoCompute();  ///< stop disparity computing 
    cam.stopCapture();  ///< stop camera capturing
    writer.release();
    return 0;
}

# 查找图片中人物
# winface for windows
# By Luckykeeper <https://luckykeeper.site|luckykeeper@luckykeeper.site> at 2022-04-08

import face_recognition
import cv2
import numpy as np
import os
import sqlite3
import msvcrt # 按键退出
import io
## 基本设定
# 人脸数据库位置，没有会自动创建
dbLoc = "./FaceDemoTest.db"
# 调试模式，True 开，False 关
debug = True
picDir = "./known/"
# picDir = "./test/"

# rtsp 视频流设定
rtsp = 'rtsp://admin:admin@177.229.21.164:8554/live'
# rtsp = "./VID_20220411_102806.mp4"
# 非数据库版导入参数
# known_face_encodings =[]
# known_face_names = []
# 初始化变量
face_locations = []
face_encodings = []
face_names = []
process_this_frame = True
# 照片导入计数变量
pic_num = 1

# 遍历照片方法
def show_files(path, all_files):
    # 首先遍历当前目录所有文件及文件夹
    file_list = os.listdir(path)
    # 准备循环判断每个元素是否是文件夹还是文件，是文件的话，把名称传入list，是文件夹的话，递归
    for file in file_list:
        # 利用os.path.join()方法取得路径全名，并存入cur_path变量，否则每次只能遍历一层目录
        cur_path = os.path.join(path, file)
        # 判断是否是文件夹
        if os.path.isdir(cur_path):
            show_files(cur_path, all_files)
        else:
            all_files.append(file)

    return all_files

def adapt_array(arr):
    out = io.BytesIO()
    np.save(out, arr)
    out.seek(0)
    return sqlite3.Binary(out.read())

def convert_array(text):
    out = io.BytesIO(text)
    out.seek(0)
    return np.load(out)

# Converts np.array to TEXT when inserting
sqlite3.register_adapter(np.ndarray, adapt_array)

# Converts TEXT to np.array when selecting
sqlite3.register_converter("array", convert_array)

# 传入空的list接收文件名
contents = show_files(picDir, [])

print("--------------------------------------------------------------------------------------")
print("Powered By Luckykeeper <https://luckykeeper.site|luckykeeper@luckykeeper.site>")
print("人脸识别 Demo 版开始运行！")
print("当前设定信息")
if debug:
    print("调试模式:ON!")
else:
    print("调试模式:OFF!")
print("人脸数据库 FaceDemo 文件位置: ",dbLoc)
print("人脸照片位置: ",picDir)
print("--------------------------------------------------------------------------------------")

if os.path.exists(dbLoc):
    try:
        FaceDemo_conn = sqlite3.connect(dbLoc, detect_types=sqlite3.PARSE_DECLTYPES)
        print("人脸数据库连接成功!")
    except:
        print("请检查人脸数据库位置设定!")

    if debug == True:
        print("数据库已经存在,读取人脸数据!")

    print ("开始初始化变量")
    notFirstRun = True
    known_face_encodings =[]
    known_face_names = []
    print ("初始化变量完成!")

    # sql 查询语句
    sqlRead = "SELECT personid, faceencode from facedemo"

    FaceDemo_cursor = FaceDemo_conn.cursor()
    personData = FaceDemo_cursor.execute(sqlRead)
    for row in personData:
        # print("导入学工号: ",row[0])
        # np_known_face_encodings = np.array(row[1])
        np_known_face_encodings = np.array([float(x) for x in row[1].split(',')])
        # print("array: ",np_known_face_encodings)
        # print("导入人脸特征: ",np_known_face_encodings,type(np_known_face_encodings))
        known_face_encodings.append(np_known_face_encodings)
        known_face_names.append(row[0])


else:
    if debug == True:
        print("没有检测到数据库,开始人脸数据导入!")
    notFirstRun = False
    
    try:
        FaceDemo_conn = sqlite3.connect(dbLoc, detect_types=sqlite3.PARSE_DECLTYPES)
        print("人脸数据库连接成功!")
    except:
        print("请检查人脸数据库位置设定!")

    print ("正在创建并初始化人脸数据库,因为照片量大,第一次初始化将花费相当长的时间,请耐心等待初始化完成!")
    FaceDemo_cursor = FaceDemo_conn.cursor()
    # personid 学号，输出名称； faceencode 人脸特征值
    FaceDemo_cursor.execute("create table facedemo(personid text,faceencode text);")
    print("数据库字段初始化完成!")
    print("--------------------------------------------------------------------------------------")
    print("开始加载人脸特征!")
    for content in contents:
        try:
            # print(content)
            print ("__________________ ")
            print("开始提取第 ",pic_num," 张照片特征值")
    
            picLoc = picDir+content
            picName = str(content)[:-4]
            print ("人脸照片位置 ",picLoc)
            print ("学工号 ",picName)
            person_img = face_recognition.load_image_file(picLoc)

            # 非数据库版导入参数
            # known_face_encodings.append(face_recognition.face_encodings(person_img)[0])
            # known_face_names.append(picName)

            # 数据库版导入参数
            known_face_encodings = face_recognition.face_encodings(person_img)[0]
            known_face_names =picName
            print("第 ",pic_num," 张照片特征值提取完成!")
            if debug:
                print("人脸特征值: ",known_face_encodings,type(known_face_encodings))

            # text_known_face_encodings = known_face_encodings.tostring()
        
            known_face_encodings_str = ','.join(str(x) for x in known_face_encodings)

            # 生成导入用 sql 语句
            sqlInsert = "insert into facedemo values ('%s','%s')" % (picName,known_face_encodings_str)
            # if debug:
                # print("sql导入语句: ",sqlInsert)
            FaceDemo_cursor.execute(sqlInsert)
            FaceDemo_conn.commit()
        
            print ("添加照片: ",picLoc," 完成!")
            pic_num = pic_num+1
            print ("__________________ ")
        except:
            print ("这个人不对劲!")

if notFirstRun == False:
    print ("数据库初始化完成!请按 Enter (回车) 键后等待退出!然后重新运行本程序开始识别!")

    while True:
        # print(str(ord(msvcrt.getch())))
        if str(ord(msvcrt.getch())) == "13":
            print ("您已按下 Enter ,请等待程序退出!")
            break
else:
    # opencv 从 rtsp 源拿数据
    video_capture = cv2.VideoCapture(rtsp)

    # print ("照片库: ",known_face_encodings,type(known_face_encodings))
    # print ("学工号库: ",known_face_names,type(known_face_names))
    while True:
        # Grab a single frame of video
        ret, frame = video_capture.read()
        # print("debug ",frame)

        # Resize frame of video to 1/4 size for faster face recognition processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        # small_frame = cv2.resize(frame, (0, 0), fx=1.0, fy=1.0)
        # small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25, interpolation = cv2.INTER_CUBIC)
        # small_frame = frame

        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        rgb_small_frame = small_frame[:, :, ::-1]
        # rgb_small_frame = small_frame

        # Only process every other frame of video to save time
        if process_this_frame:
            # Find all the faces and face encodings in the current frame of video
            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

            face_names = []
            for face_encoding in face_encodings:
                # See if the face is a match for the known face(s)
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                name = "Unknown"

                # # If a match was found in known_face_encodings, just use the first one.
                # if True in matches:
                #     first_match_index = matches.index(True)
                #     name = known_face_names[first_match_index]

                # Or instead, use the known face with the smallest distance to the new face
                face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = known_face_names[best_match_index]

                face_names.append(name)

        process_this_frame = not process_this_frame


        # Display the results
        for (top, right, bottom, left), name in zip(face_locations, face_names):
            # Scale back up face locations since the frame we detected in was scaled to 1/4 size
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            # Draw a box around the face
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 127), 2)

            # Draw a label with a name below the face
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 255, 127), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

        # Display the resulting image
        cv2.imshow('FaceDemo By Luckykeeper', frame)

        # Hit 'q' on the keyboard to quit!
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release handle to the webcam
    video_capture.release()
    cv2.destroyAllWindows()
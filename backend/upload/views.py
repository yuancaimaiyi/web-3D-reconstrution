from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status, serializers
from .serializers import DatasetSerializer, ImageSerializer
from .models import Dataset, Image
from django.utils import timezone, text, dateformat
from django.conf import settings
from django.http import HttpResponse, FileResponse, JsonResponse
import os
import zipfile
import shutil
from io import BytesIO
from pathlib import Path
# from .visualize_model import Model
import subprocess
import socket
import time
class UploadView(APIView):
    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser, FormParser)

    def get(self, request, *args, **kwargs):
        datasets = Dataset.objects.all()
        serializer = DatasetSerializer(datasets, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        # Convert QueryDict to Python's dict
        images = dict(request.data.lists())['images']
        print(f"file number: {len(images)}\n")
        timestamp = timezone.now()
        dataset_serializer = DatasetSerializer(
            data={
                'user': request.user.id,
                'dataset_path': 'datasets/user_{}_{}'.format(request.user.id, text.slugify(timestamp)),
                'images_count': len(images),
                'created_at': timestamp,
                'status': 0,
                'comment': 'Waiting'
            }
        )
        dataset_serializer.is_valid(raise_exception=True)
        dataset_instance = dataset_serializer.save()

        try:
            for image in images:
                wrapped_image = {
                    'dataset': dataset_instance.id,
                    'image': image
                }
                if image.content_type.startswith('image/'):
                    image_serializer = ImageSerializer(data=wrapped_image)
                    image_serializer.is_valid(raise_exception=True)
                    image_serializer.save()
                elif image.content_type == 'application/json':
                    json_content = image.read()
                    img_path = settings.MEDIA_ROOT / dataset_instance.dataset_path
                    json_filename = image.name
                    json_path = os.path.join(img_path, json_filename)
                    with open(json_path, 'wb') as json_file:
                        json_file.write(json_content)
                    # json_content_str = json_content.decode('utf-8') 
                    # print(json_content_str)
        except serializers.ValidationError:
            Image.objects.filter(dataset=dataset_instance.id).delete()
            update = Dataset.objects.get(id=dataset_instance.id)
            if update:
                update.comment = 'Bad pictures'
                update.save()

            return Response('Incorrect name or value of pictures', status=status.HTTP_400_BAD_REQUEST)

        # Launch vismap
        update = Dataset.objects.get(id=dataset_instance.id)
        if update:
            update.comment = 'In progress'
            update.save()

        img_path = settings.MEDIA_ROOT / dataset_instance.dataset_path
        # print("=======================================\n")
        # print(settings.MEDIA_ROOT )
        # print(dataset_instance.dataset_path)
        # print("=======================================\n")
        python3_result_code = os.system('python3 -V')
        if python3_result_code == 0:
            python_version = 'python3'
        else:
            python_version = 'python'
        fileNum  =  len(os.listdir(img_path))
        imageNum = 0
        for file in os.listdir(img_path):
             if file.endswith("jpg") or file.endswith("png"):
                 imageNum += 1
        if fileNum != imageNum:
            print("3D scanner  app  file....\n")
            print(f'fsba : {settings.FSBA}, vision: {settings.PURE_VISION}\n')
            print("Run launch_vismap.py \n")
            sfm = os.system(python_version + ' /app/hera-vismap/script/launch_vismap.py \
                                    {} \
                                    {} \
                                    {}'.format(img_path,settings.FSBA,settings.PURE_VISION))
            print("vismap sfm finished......\n")
            print("===============================\n")
            print("Begin learned-feature map building......\n")
            postprocess_sfm = os.system(python_version + "  /app/hera-vismap/script/featuremanage/preprocess_images.py \
                                        --assets_path {}     --ext {}".format(os.path.join(settings.MEDIA_ROOT,dataset_instance.dataset_path.split("/")[0]) , 
                                                                            dataset_instance.dataset_path.split("/")[-1]))
            
            build_scene = os.system(python_version + "  /app/hera-vismap/script/featuremanage/build_scene_images.py \
                                        --assets_path {}     --ext {}".format(os.path.join(settings.MEDIA_ROOT,dataset_instance.dataset_path.split("/")[0]) , 
                                                                            dataset_instance.dataset_path.split("/")[-1]))
            print("vismap long-term map building finished ......\n")
            
        else:
            print("Only  images file ....\n")
            print(f'fsba : {settings.FSBA}, vision: {settings.PURE_VISION}\n')
            print("Run launch_vismap_images.py\n")      
            sfm = os.system(python_version + ' /app/hera-vismap/script/launch_vismap_images.py\
                                    {} \
                                    {} \
                                    {}'.format(img_path,settings.FSBA,settings.PURE_VISION))
            print("vismap sfm finished......\n")
            print("===============================\n")
            print("Begin learned-feature map building......\n")
            postprocess_sfm = os.system(python_version + "  /app/hera-vismap/script/featuremanage/preprocess_images.py \
                                        --assets_path {}     --ext {}".format(os.path.join(settings.MEDIA_ROOT,dataset_instance.dataset_path.split("/")[0]) , 
                                                                            dataset_instance.dataset_path.split("/")[-1]))
            
            build_scene = os.system(python_version + "  /app/hera-vismap/script/featuremanage/build_scene_images.py \
                                       --assets_path {}     --ext {}".format(os.path.join(settings.MEDIA_ROOT,dataset_instance.dataset_path.split("/")[0]) , 
                                                                            dataset_instance.dataset_path.split("/")[-1]))
            print("vismap long-term map building finished ......\n")        
        if  build_scene ==0 :
            try:
                user_folder = 'user_{}_{}'.format(request.user.id, text.slugify(timestamp))

                # response = {
                #     'obj': '/media/datasets/' + user_folder + '/result/texturedMesh.obj',
                #     'png': '/media/datasets/' + user_folder + '/result/texture_1001.png'
                # }
                response ={ 'sfm': f'{settings.MEDIA_ROOT }/ "datasets"/{user_folder}_6dof'}

                # with open(Path.joinpath(img_path, 'result', 'texturedMesh.obj'), "r") as f:
                #     response['obj'] = f.read()
                #
                # with open(Path.joinpath(img_path, 'result', 'texturedMesh.mtl'), "r") as f:
                #     response['mtl'] = f.read()

                update = Dataset.objects.get(id=dataset_instance.id)
                if update:
                    update.comment = 'Complete'
                    update.save()

                return JsonResponse(response, status=status.HTTP_200_OK)

            except FileNotFoundError:
                update = Dataset.objects.get(id=dataset_instance.id)
                if update:
                    update.comment = 'Error'
                    update.save()

                Image.objects.filter(dataset=dataset_instance.id).delete()

                return Response('Result file was not found', status=status.HTTP_404_NOT_FOUND)

        else:
            update = Dataset.objects.get(id=dataset_instance.id)
            if update:
                update.comment = 'Error'
                update.save()

            Image.objects.filter(dataset=dataset_instance.id).delete()

            return Response('vismap internal error', status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# class StatusView(APIView):
#     permission_classes = (IsAuthenticated,)
#     parser_classes = (MultiPartParser, FormParser)

#     def get(self, request, *args, **kwargs):

#         # Get all user's projects in DB
#         dataset_instance = Dataset.objects.filter(user=request.user.id).order_by('created_at')

#         # # Folders, which Meshroom create with current pipeline
#         # folders = ["CameraInit",
#         #            "FeatureExtraction",
#         #            "ImageMatching",
#         #            "FeatureMatching",
#         #            "StructureFromMotion",
#         #            "Meshing",
#         #            "MeshFiltering",
#         #            "Texturing",
#         #            "Publish"]

#         # Every meshroom step have corresponding status, "Comlete" status is amount of all steps + 1
#         # complete_status = len(folders) + 1
#         complete_status =  10 
#         print ( "worker num : {}\n".format(dataset_instance.count()))
#         for i in range(dataset_instance.count()):

#             try:
#                 img_path = settings.MEDIA_ROOT / dataset_instance[i].dataset_path

#                 # # Check 'cache' folder: if no folder and status 0 - valid, if no folder and status not 0 - invalid
#                 # if 'cache' not in os.listdir(path=img_path):
#                 #     if dataset_instance[i].status == 0:
#                 #         continue
#                 #     else:
#                 #         update = Dataset.objects.get(id=dataset_instance[i].id)
#                 #         if update:
#                 #             update.comment = 'Error'
#                 #             update.save()

#                 # If project have last status and result with files exist in local - valid, if no result - invalid
#                 if dataset_instance[i].comment == 'Complete':
#                     if 'images.txt'  or  'images.bin' in os.listdir(path=Path(img_path + '_sfm' / 'map' / 'sparse_model')) and len(
#                             os.listdir(path=Path(img_path + '_sfm'))) >= 2:
#                         dataset_instance[i].status == complete_status
#                     else:
#                         update = Dataset.objects.get(id=dataset_instance[i].id)
#                         if update:
#                             update.comment = 'Error'
#                             update.save()

#                 # # Update curr project status
#                 # for curr_status in range(1, complete_status):
#                 #     numeric_folder = os.listdir(path=Path.joinpath(img_path, 'cache', folders[curr_status - 1]))[0]
#                 #     # In this folders file "status" is already exist, if that's all, this step in progress
#                 #     if len(os.listdir(
#                 #             path=Path.joinpath(img_path, 'cache', folders[curr_status - 1], numeric_folder))) < 2:
#                 #         update = Dataset.objects.get(id=dataset_instance[i].id)
#                 #         if update:
#                 #             update.status = curr_status
#                 #             update.save()
#                 #         break

#                 # Give last status if result exist
#                 if 'images.txt'  or  'images.bin' in os.listdir(path=Path(img_path + '_sfm' / 'map' / 'sparse_model')) and len(
#                     os.listdir(path=Path(img_path + '_sfm'))) >= 2:
#                     update = Dataset.objects.get(id=dataset_instance[i].id)
#                     if update:
#                         update.status = complete_status
#                         update.save()

#             # If folder with dataset, cache or result doesn't exist, but DB gave info about it
#             except FileNotFoundError:
#                 update = Dataset.objects.get(id=dataset_instance[i].id)
#                 if update:
#                     update.comment = 'Error'
#                     update.save()
#                 continue

#         projects = []

#         for i in range(dataset_instance.count()):

#             project = {'Created_at': dateformat.format(dataset_instance[i].created_at, "M j Y H:i:s"),
#                        'Status': "{}".format(int(dataset_instance[i].status * (1 / complete_status) * 100)),
#                        'Comment': dataset_instance[i].comment,
#                        'Is_removable': False}

#             if dataset_instance[i].comment == 'Complete':
#                 project['Download_url'] = "http://localhost:8000/upload/download/?project=user_{}_{}".format(request.user.id, text.slugify(dataset_instance[i].created_at))

#             if dataset_instance[i].comment != 'Waiting' and dataset_instance[i].comment != 'In progress':
#                 project['Is_removable'] = True
#                 project['Remove_url'] = "http://localhost:8000/upload/remove/?project=user_{}_{}".format(request.user.id, text.slugify(dataset_instance[i].created_at))

#             projects.append(project)

#         response = {'projects': projects}

#         return JsonResponse(response, status=status.HTTP_200_OK)
class StatusView(APIView):
    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser, FormParser)
    def getdirsize( self,path):
        size = 0
        for root, dirs, files in os.walk(path):
            size += sum([os.path.getsize(os.path.join(root, name)) for name in files])
        # M
        return size / (1024 * 1024)

    def get(self, request, *args, **kwargs):

        # Get all user's projects in DB
        dataset_instance = Dataset.objects.filter(user=request.user.id).order_by('created_at')
        complete_status = 100
        print(f'worker num : {dataset_instance.count()}\n')
        for i in range(dataset_instance.count()):

            try:
                img_path = settings.MEDIA_ROOT / dataset_instance[i].dataset_path
                sparse_model  =  Path(str(img_path) + '_sfm') / 'map' / 'sparse_model'
                print (f'sfm result path :{sparse_model}\n')
                print("\n")
                ar_model  =  Path(str(img_path) + '_6dof') / 'sfm_superpoint+superglue' / 'model'
                os.makedirs(ar_model, exist_ok=True)
                print (f'AR map  path :{ar_model}\n')
                print("\n")
                if  'images.txt' in os.listdir(ar_model) or 'images.bin' in os.listdir(ar_model) :
                    update = Dataset.objects.get(id=dataset_instance[i].id)
                    if update:
                        update.status = complete_status
                        update.save()

            # If folder with dataset, cache or result doesn't exist, but DB gave info about it
            except FileNotFoundError:
                update = Dataset.objects.get(id=dataset_instance[i].id)
                if update:
                    update.comment = 'Error'
                    update.save()
                continue

        projects = []

        for i in range(dataset_instance.count()):

            project = {'Created_at': dateformat.format(dataset_instance[i].created_at, "M j Y H:i:s"),
                       'Status': "{}".format(int(dataset_instance[i].status)),
                       'Comment': dataset_instance[i].comment,
                       'Is_removable': False}

            if dataset_instance[i].comment == 'Complete':
                project['Download_url'] = "http://localhost:8000/upload/download/?project=user_{}_{}".format(request.user.id, text.slugify(dataset_instance[i].created_at))
                project['View_url'] = "http://localhost:8000/upload/view/?project=user_{}_{}".format(request.user.id, text.slugify(dataset_instance[i].created_at))

            if dataset_instance[i].comment != 'Waiting' and dataset_instance[i].comment != 'In progress':
                project['Is_removable'] = True
                project['Remove_url'] = "http://localhost:8000/upload/remove/?project=user_{}_{}".format(request.user.id, text.slugify(dataset_instance[i].created_at))

            projects.append(project)

        response = {'projects': projects}

        return JsonResponse(response, status=status.HTTP_200_OK)
class ViewView(APIView):
    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser, FormParser)
    def __init__(self):
        super().__init__()
        self.get_request_counter = 0  # Initialize a counter for get requests
    def get(self, request, *args, **kwargs):
        self.get_request_counter += 1
        project = request.GET.get('project', '')
        # If key 'project' doesn't exist
        if project == '':
            return Response('Bad Request', status=status.HTTP_400_BAD_REQUEST)

        project_info = project.split("_")

        # If user in 'project' doesn't match with user in authorization key
        if len(project_info) != 3 or project_info[0] != 'user' or project_info[1] != str(request.user.id):
            return Response('Wrong user', status=status.HTTP_403_FORBIDDEN)

        dataset_instance = Dataset.objects.filter(user=request.user.id).filter(dataset_path="datasets/" + project)

        # If there is no 'project' in DB
        if not dataset_instance:
            return Response('Result file was not found', status=status.HTTP_404_NOT_FOUND)

        try:
            sparse_model  = Path.joinpath(settings.MEDIA_ROOT, 'datasets', project+"_sfm",'map','sparse_model')
            reconstruction_json =  Path.joinpath(settings.MEDIA_ROOT, 'datasets', project+"_sfm",'map')
            print(f'sparse model : {sparse_model}\n')
            # model = Model()
            # model.read_model(sparse_model)
            # print("num_cameras:", len(model.cameras))
            # print("num_images:", len(model.images))
            # print("num_points3D:", len(model.points3D))
            initPort = 8085
            flask_command = [
                'python3', '/app/viewer/server.py', '-d', str(reconstruction_json) ,  '-p',  str(initPort + self.get_request_counter) 
            ]
            subprocess.Popen(flask_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            time.sleep(1)
            print(f'Flask server started: {reconstruction_json}\n')
            host_ip = socket.gethostbyname(socket.gethostname())
            frontend_url =  f"http://{host_ip}:{initPort + self.get_request_counter}"
            print(f'viewer url : {frontend_url}\n') 
            return JsonResponse({'frontend_url': frontend_url})

            # python3_result_code = os.system('python3 -V')
            # if python3_result_code == 0:
            #     python_version = 'python3'
            # else:
            #     python_version = 'python'
            # initPort = 8085
            # result = os.system(python_version + ' /app/viewer/server.py   -d  {}   -p  {}'.format(reconstruction_json, initPort + self.get_request_counter ))       
            # if result == 0 :
            #     print(f'viewer  path : {reconstruction_json}\n')
            #     webbrowser.open("http://localhost:8085")
            #     pass   
            # display using Open3D visualization tools
            # model.create_window()
            # model.add_points()
            # model.add_cameras(scale=0.25)
            # model.show()
        except FileNotFoundError:
            return Response('sparse model  file was not found', status=status.HTTP_404_NOT_FOUND)
class DownloadView(APIView):
    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser, FormParser)

    def get(self, request, *args, **kwargs):

        project = request.GET.get('project', '')
        # If key 'project' doesn't exist
        if project == '':
            return Response('Bad Request', status=status.HTTP_400_BAD_REQUEST)

        project_info = project.split("_")

        # If user in 'project' doesn't match with user in authorization key
        if len(project_info) != 3 or project_info[0] != 'user' or project_info[1] != str(request.user.id):
            return Response('Wrong user', status=status.HTTP_403_FORBIDDEN)

        dataset_instance = Dataset.objects.filter(user=request.user.id).filter(dataset_path="datasets/" + project)

        # If there is no 'project' in DB
        if not dataset_instance:
            return Response('Result file was not found', status=status.HTTP_404_NOT_FOUND)

        try:
            # # TODO: Maybe there are several .png files. You should consider this case.
            # filenames = ['texturedMesh.obj', 'texture_1001.png']

            # # Folder name in ZIP archive which contains the above files
            # # E.g [thearchive.zip]/dirname/abracadabra.txt
            # zip_subdir = "/"

            # bytes_stream = BytesIO()
            # with zipfile.ZipFile(bytes_stream, 'w') as zip_file:
            #     for filename in filenames:
            #         filepath = Path.joinpath(settings.MEDIA_ROOT, 'datasets', project, 'result', filename)
            #         zip_filepath = os.path.join(zip_subdir, filename)
            #         zip_file.write(filepath, zip_filepath)
            folder_to_compress = Path.joinpath(settings.MEDIA_ROOT, 'datasets', project+"_6dof")
            print(f'compess sfm folder :  {folder_to_compress} \n ')
            if not os.path.exists(folder_to_compress):
                return Response("Project sfm folder not found",status=status.HTTP_404_NOT_FOUND)
            with zipfile.ZipFile('sfm.zip', 'w') as zip_file:
                for foldername, subfolders, filenames in os.walk(folder_to_compress):
                    for filename in filenames:
                        file_path = os.path.join(foldername, filename)
                        zip_path = os.path.relpath(file_path, folder_to_compress)
                        zip_file.write(file_path, zip_path)
                # 将ZIP文件作为HTTP响应返回
            with open('sfm.zip', 'rb') as zip_file:
                response = HttpResponse(zip_file.read(), content_type='application/zip')
                response['Content-Disposition'] = 'attachment; filename="sfm.zip"'  # 设置下载文件的名称

            # response = HttpResponse(bytes_stream.getvalue(),
            #                         content_type='application/zip',
            #                         status=status.HTTP_200_OK)

            return response

        # If file not found in local server
        except FileNotFoundError:
            return Response('Result file was not found', status=status.HTTP_404_NOT_FOUND)


class RemoveView(APIView):
    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser, FormParser)

    def get(self, request, *args, **kwargs):

        project = request.GET.get('project', '')
        # If key 'project' doesn't exist
        if project == '':
            return Response('Bad Request', status=status.HTTP_400_BAD_REQUEST)

        project_info = project.split("_")

        # If user in 'project' doesn't match with user in authorization key
        if len(project_info) != 3 or project_info[0] != 'user' or project_info[1] != str(request.user.id):
            return Response('Wrong user', status=status.HTTP_403_FORBIDDEN)

        dataset_instance = Dataset.objects.filter(user=request.user.id).filter(dataset_path="datasets/" + project)

        # If there is no 'project' in DB
        if not dataset_instance:
            return Response('Object was not found', status=status.HTTP_404_NOT_FOUND)

        # Delete project folder with all content
        shutil.rmtree(Path.joinpath(settings.MEDIA_ROOT, 'datasets', project), ignore_errors=True)
        shutil.rmtree(Path.joinpath(settings.MEDIA_ROOT, 'datasets', project + "_calibration"), ignore_errors=True)
        shutil.rmtree(Path.joinpath(settings.MEDIA_ROOT, 'datasets', project+"_images"), ignore_errors=True)
        shutil.rmtree(Path.joinpath(settings.MEDIA_ROOT, 'datasets', project+"_sfm"), ignore_errors=True)
        shutil.rmtree(Path.joinpath(settings.MEDIA_ROOT, 'datasets', project+"_6dof"), ignore_errors=True)
        # Delete project object from 'Dataset' table, which will cause deletion of all connected objects
        dataset_instance.delete()
        return Response(f'The {project} was removed', status=status.HTTP_200_OK)

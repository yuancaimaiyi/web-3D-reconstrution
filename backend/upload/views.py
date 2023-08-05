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
                image_serializer = ImageSerializer(data=wrapped_image)
                image_serializer.is_valid(raise_exception=True)
                image_serializer.save()

        except serializers.ValidationError:
            Image.objects.filter(dataset=dataset_instance.id).delete()
            update = Dataset.objects.get(id=dataset_instance.id)
            if update:
                update.comment = 'Bad pictures'
                update.save()

            return Response('Incorrect name or value of pictures', status=status.HTTP_400_BAD_REQUEST)

        # Launch Meshroom
        update = Dataset.objects.get(id=dataset_instance.id)
        if update:
            update.comment = 'In progress'
            update.save()

        img_path = settings.MEDIA_ROOT / dataset_instance.dataset_path
        python3_result_code = os.system('python3 -V')
        if python3_result_code == 0:
            python_version = 'python3'
        else:
            python_version = 'python'
        meshroom_result_code = os.system(python_version + ' launch.py \
                                   Meshroom \
                                   pipeline_graph_template.mg \
                                   {}'.format(img_path))

        if meshroom_result_code == 0:
            try:
                user_folder = 'user_{}_{}'.format(request.user.id, text.slugify(timestamp))

                response = {
                    'obj': '/media/datasets/' + user_folder + '/result/texturedMesh.obj',
                    'png': '/media/datasets/' + user_folder + '/result/texture_1001.png'
                }

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

            return Response('Meshroom internal error', status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class StatusView(APIView):
    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser, FormParser)

    def get(self, request, *args, **kwargs):

        # Get all user's projects in DB
        dataset_instance = Dataset.objects.filter(user=request.user.id).order_by('created_at')

        # Folders, which Meshroom create with current pipeline
        folders = ["CameraInit",
                   "FeatureExtraction",
                   "ImageMatching",
                   "FeatureMatching",
                   "StructureFromMotion",
                   "Meshing",
                   "MeshFiltering",
                   "Texturing",
                   "Publish"]

        # Every meshroom step have corresponding status, "Comlete" status is amount of all steps + 1
        complete_status = len(folders) + 1

        for i in range(dataset_instance.count()):

            try:
                img_path = settings.MEDIA_ROOT / dataset_instance[i].dataset_path

                # Check 'cache' folder: if no folder and status 0 - valid, if no folder and status not 0 - invalid
                if 'cache' not in os.listdir(path=img_path):
                    if dataset_instance[i].status == 0:
                        continue
                    else:
                        update = Dataset.objects.get(id=dataset_instance[i].id)
                        if update:
                            update.comment = 'Error'
                            update.save()

                # If project have last status and result with files exist in local - valid, if no result - invalid
                if dataset_instance[i].comment == 'Complete':
                    if 'result' in os.listdir(path=img_path) and len(
                            os.listdir(path=Path.joinpath(img_path, 'result'))) >= 3:
                        if dataset_instance[i].status == complete_status:
                            continue
                    else:
                        update = Dataset.objects.get(id=dataset_instance[i].id)
                        if update:
                            update.comment = 'Error'
                            update.save()

                # Update curr project status
                for curr_status in range(1, complete_status):
                    numeric_folder = os.listdir(path=Path.joinpath(img_path, 'cache', folders[curr_status - 1]))[0]
                    # In this folders file "status" is already exist, if that's all, this step in progress
                    if len(os.listdir(
                            path=Path.joinpath(img_path, 'cache', folders[curr_status - 1], numeric_folder))) < 2:
                        update = Dataset.objects.get(id=dataset_instance[i].id)
                        if update:
                            update.status = curr_status
                            update.save()
                        break

                # Give last status if result exist
                if 'result' in os.listdir(path=img_path) and len(
                        os.listdir(path=Path.joinpath(img_path, 'result'))) >= 3:
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
                       'Status': "{}".format(int(dataset_instance[i].status * (1 / complete_status) * 100)),
                       'Comment': dataset_instance[i].comment,
                       'Is_removable': False}

            if dataset_instance[i].comment == 'Complete':
                project['Download_url'] = "http://localhost:8000/upload/download/?project=user_{}_{}".format(request.user.id, text.slugify(dataset_instance[i].created_at))

            if dataset_instance[i].comment != 'Waiting' and dataset_instance[i].comment != 'In progress':
                project['Is_removable'] = True
                project['Remove_url'] = "http://localhost:8000/upload/remove/?project=user_{}_{}".format(request.user.id, text.slugify(dataset_instance[i].created_at))

            projects.append(project)

        response = {'projects': projects}

        return JsonResponse(response, status=status.HTTP_200_OK)


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
            # TODO: Maybe there are several .png files. You should consider this case.
            filenames = ['texturedMesh.obj', 'texture_1001.png']

            # Folder name in ZIP archive which contains the above files
            # E.g [thearchive.zip]/dirname/abracadabra.txt
            zip_subdir = "/"

            bytes_stream = BytesIO()
            with zipfile.ZipFile(bytes_stream, 'w') as zip_file:
                for filename in filenames:
                    filepath = Path.joinpath(settings.MEDIA_ROOT, 'datasets', project, 'result', filename)
                    zip_filepath = os.path.join(zip_subdir, filename)
                    zip_file.write(filepath, zip_filepath)

            response = HttpResponse(bytes_stream.getvalue(),
                                    content_type='application/zip',
                                    status=status.HTTP_200_OK)

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

        # Delete project object from 'Dataset' table, which will cause deletion of all connected objects
        dataset_instance.delete()

        return Response('The object was removed', status=status.HTTP_200_OK)

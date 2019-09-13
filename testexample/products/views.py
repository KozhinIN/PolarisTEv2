from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import ProductSerializer, ProductReadSerializer, \
                         PenSerializer, PencilSerializer, PaperSerializer
from .models import Product

class ProductListView (APIView):
    """
    View to list all products or paginated list of products,
    or create a new product
    """
    def get(self, request):
        """
        list products
        request body:
        count - number of products per page
        shift - requested page (start from 0)
        """
        data = request.data
        if data.get('count', False) and data.get('shift', False):
            left = int(data['shift']) * int(data['count'])
            rigth = int(data['shift']) * int(data['count']) + int(data['count'])
            products = Product.objects.all()[left:rigth]
        else:
            products = Product.objects.all()
        serializer = ProductReadSerializer(products, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        """
        request body:
        title: string
        brand: string
        vendorcode: unique str
        price: number
        description: text

        optional ( 1 of 3):
        * var: 1 pencil
            color: string
            hardness: string
        * var 2 pen
            color: string
            type: choisefield
        * var 3 paper
            format: string
            sheets: number

        if several options are provided, the first will disappear
        """
        data = request.data.copy()
        variant = 0
        #Проверяем шаблон
        if data.get('color', False) and data.get('type', False):
            variant = 1
        elif data.get('color', False) and data.get('hardness', False):
            variant = 2
        elif data.get('format', False) and data.get('sheets', False):
            variant = 3
        # Если данные соответствую одном из шаблонов -> создаем
        if variant:
            product_serializer = ProductSerializer(data=data)
            if product_serializer.is_valid():
                product_serializer.save()
                data['product']=product_serializer.data['id']
                print(data)
            else:
                return Response(product_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            # Выбор сериализатора
            if variant == 1:
                det_serializer = PenSerializer(data=data)
            elif variant == 2:
                det_serializer = PencilSerializer(data=data)
            elif variant == 3:
                det_serializer = PaperSerializer(data=data)

            if det_serializer.is_valid():
                det_serializer.save()
                answer = {
                    'product': product_serializer.data,
                    'detail': det_serializer.data
                }
                return Response(answer, status=status.HTTP_201_CREATED)
            else:
                return Response(det_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response('Not all field entered', status=status.HTTP_400_BAD_REQUEST)

class ProductDetailView (APIView):
    """
    Retrive, update and delete product
    """
    def get_object(self, pk):
        try:
            return Product.objects.select_related().get(pk=pk)
        except Product.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        """
        Retrive product
        :param request: none
        :param pk: number
        """
        product = self.get_object(pk)
        serializer = ProductReadSerializer(product)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        """
        Update product info

        request body:
        title: string
        brand: string
        vendorcode: unique str
        price: number
        description: text

        optional ( 1 of 3):
        * var: 1 pencil
            color: string
            hardness: string
        * var 2 pen
            color: string
            type: choisefield
        * var 3 paper
            format: string
            sheets: number

        *if several options are provided, the first will disappear
        """
        product = self.get_object(pk)
        data = request.data.copy()
        data['product']=product.id
        variant = 0
        table = 0
        # Определяем существующую запись
        try:
            product.pendetail
        except:
            pass
        else:
            table = 1
        try:
            product.pencildetail
        except:
            pass
        else:
            table = 2
        try:
            product.paperdetail
        except:
            pass
        else:
            table = 3

        # Проверяем шаблон
        if data.get('color', False) and data.get('type', False):
            det_serializer = PenSerializer(data=data)
            variant = 1
        elif data.get('color', False) and data.get('hardness', False):
            det_serializer = PencilSerializer(data=data)
            variant = 2
        elif data.get('format', False) and data.get('sheets', False):
            det_serializer = PaperSerializer(data=data)
            variant = 3

        # Удаление и создание или изменение
        if variant and table:
            if variant != table:
                if table == 1:
                    product.pendetail.delete()
                elif table == 2:
                    product.pencildetail.delete()
                elif table == 3:
                    product.paperdetail.delete()
                if det_serializer.is_valid():
                    det_serializer.save()
                else:
                    return Response(det_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                if table == 1:
                    product.pendetail.color = data['color']
                    product.pendetail.type = data['type']
                    product.pencildetail.save()
                elif table == 2:
                    product.pencildetail.color = data['color']
                    product.pencildetail.hardness = data['hardness']
                    product.pencildetail.save()
                elif table == 3:
                    product.paperdetail.format = data['format']
                    product.paperdetail.sheets = data['sheets']
                    product.paperdetail.save()

        #Обновление данных
        product = self.get_object(pk)
        serializer = ProductReadSerializer(product, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response('Smthing go wrong', status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        """
        delete product
        :param pk: number
        """
        product = self.get_object(pk)
        print(product)
        product.delete()
        return Response('delete success', status=status.HTTP_204_NO_CONTENT)

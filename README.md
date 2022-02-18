# Foodalways
A copy of the food making tutorial and food picture website. Original repo: https://github.com/fandiandian/fansfood

Front end use: Bootstrap build<br>
Back-end development environment: python3.6.2 + django2.2 + xadmin2 (xadmin needs to be installed separately)<br>
Deployment: Nginx + uWSGI<br>
Website: www.foodalways.com<br>


## Website demo pages
Login page<br>
![login](#META_LOGIN_MEDIA)
Home<br>
![login](#META_HOME_MEDIA)
User Center<br>
![login](#META_UCENTER_MEDIA)


## Data Sources
Data acquisition: use requests + bs4 + re<br>
The proxy ip uses Abuyun dynamic version<br>
Website data source: Making tutorials (#META_FOOD_WEBSITE) + pictures (#META_IMAGE_WEBSITE)<br>
The location of the crawler code: foodalways/apps/assist_function/data_crawler, the saved data file path needs to be modified by yourself<br>
The crawled data is stored directly in MongoDB. According to the design of the model, it is divided and dumped to PostgreSQL<br>


## Development
### There are some problems in the adaptation of xadmin to Django2.2, and some function changes need to be made
Installation: This is the fastest, git installation is too slow<br>

    pip install https://codeload.github.com/sshwsfc/xadmin/zip/django2

Adaptation modification: see https://github.com/vip68/xadmin_bugfix
The main places I modified are the places where the following errors occur:

    TypeError at /xadmin/xadmin/userwidget/add/ render() got an unexpected keyword argument'renderer'

Refer to https://github.com/vip68/xadmin_bugfix/commit/344487d80e6ff830f39b3526ee024231921c074d to solve this problem

I clicked on each xadmin module and checked it. To be safe, I added a `renderer=None` to all `render` functions. This bug occurred without sending.<br>
This error will also be reported if the **ueditor** rich text editor is integrated, and the reason is the same

    Find UEditor/widgets.py, line 167
    --- def render(self, name, value, attrs=None):
    +++ def render(self, name, value, attrs=None, renderer=None):
    Reference: https://github.com/sshwsfc/xadmin/issues/621

Another is the modification of the background custom icon:

    The version of font-awwsome used was too low, so I changed it to version 4.7
    Overwrite the two folders under font-awesome-4.7.0 in the directory
        The directory under venv/Lib/site-packages/xadmin/static/xadmin/vendor/font-awesome is fine
    Then go to https://fontawesome.com/v4.7.0/icons/ according to your favorite


### Modification of page turning plug-in
The django third-party plugin pure-pagination is used

    Project homepage: https://github.com/jamespacileo/django-pure-pagination

Since there are two page paginations when displaying favorites in my user center, it is necessary to distinguish the corresponding keys of page pagination, and modify it as follows:

    Row 19
    --- def __init__(self, object_list, per_page, orphans=0, allow_empty_first_page=True, request=None):
    +++ def __init__(self, object_list, per_page, orphans=0, allow_empty_first_page=True, request=None, page_type='page'):
    Row 26
    +++ self.page_type = page_type
    Line 206
    --- self.base_queryset['page'] = page_number
    +++ self.base_queryset[self.page_type] = page_number
    210 rows
    --- return'page=%s'% page_number
    +++ return'{}={}'.format(self.page_type, page_number)

In this way, when the paging object is instantiated, different paging objects can be distinguished by setting the `page_type` parameter


## Development

### Installation
* Set up and enable `venv`
* Install libraries
  ```
  pip install -r requirements.txt
  ```
* Do migration
  ```
  python manage.py makemigrations
  python manage.py migrate
  ```

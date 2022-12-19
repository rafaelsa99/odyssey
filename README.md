# GeoNode Odyssey

## Table of Contents

-  [Installation](#installation)
	-  [Preparation](#preparation)
	-  [GeoNode-Project Installation without Docker](#geonode-project-installation-without-docker)
	-  [GeoNode-Project Installation with Docker](#geonode-project-installation-with-docker)
-  [Deploy on a domain](#deploy-on-a-domain)
-  [GeoNode Configuration](#geonode-configuration)
	-  [Upload Size Limits](#upload-size-limits)
	-  [Cookies Pop-up](#cookies-pop-up)
	-  [Upload INSPIRE Thesaurus](#upload-inspire-thesaurus)
	-  [Upload Layers](#upload-layers)
	-  [Add Attributes and Metric Types to the database](#add-attributes-and-metric-types-to-the-database)
-  [GeoServer Configuration](#geoserver-configuration)
	-  [Create a Data Store](#create-a-data-store)
	-  [Create Layers](#create-layers)
-  [Some Restrictions to keep in mind when using GeoNode](#some-restrictions-to-keep-in-mind-when-using-geonode)
	-  [Import Occurrences](#import-occurrences)
	-  [Automatic Identification](#automatic-identification)

## Installation

**NOTE**: *The installation assumes an Ubuntu 20.04LTS 64-bit environment.*
### Preparation

1. Install the development header files

    ```bash
    sudo apt install libmemcached-dev
    ```
2.	Install GDAL

    ```bash
    sudo apt install libpq-dev gdal-bin libgdal-dev
    ```
3.	Install virtualenvwrapper/virtualenv

    ```bash
    sudo apt-get install python3-pip
	sudo pip3 install virtualenv
	sudo pip3 install virtualenvwrapper
    ```
4.	Add the following lines to the shell startup file
    ```bash
    vim ~/.bashrc
	# Add following lines
	export WORKON_HOME=$HOME/.virtualenvs
	export PROJECT_HOME=$HOME/Devel
	export VIRTUALENVWRAPPER_PYTHON=’/usr/bin/python3’
	source /usr/local/bin/virtualenvwrapper.sh
    ```
5.	Close the file and run the following command

    ```bash
    source ~/.bashrc
    ```
### GeoNode-Project Installation without Docker

This installation method does not use Docker and is suitable for development. The installation instructions are based on the [official GeoNode documentation](https://docs.geonode.org/en/3.3.x/devel/installation/index.html#install-geonode-project-directly-from-scratch).

1.	Create a virtual environment

    ```bash
    mkvirtualenv --python=/usr/bin/python3 geonode_odyssey
	workon geonode_odyssey
    ```

2.	Clone the project from GitHub

    ```bash
    git clone https://github.com/rafaelsa99/odyssey.git
    ```

3.	Install Django framework

	```bash
    pip install Django==2.2.24
    ```

4.	Install the requirements for the GeoNode-project and install the GeoNode-project

	**NOTE**: *Errors may occur for packages that have versions that are incompatible with GeoNode. In these cases, you should reinstall each package with the respective version.*

	```bash
	mv odyssey geonode_odyssey
    cd geonode_odyssey/src/
	pip install -r requirements.txt --upgrade

	# In case of errors:
	# pip install <PACKAGE>==<VERSION> --force-reinstall

	pip install -e . --upgrade
    ```

5.	Install GDAL Utilities for Python
	```bash
    pip install pygdal=="`gdal-config --version`.*"
    ```

#### Install and Configure the PostgreSQL Database System

The installation instructions are based on the [official GeoNode documentation](https://docs.geonode.org/en/3.3.x/install/advanced/project/index.html#geonode-project-installation).

1.	Install the PostgreSQL packages along with the PostGIS extension

	**NOTE**: *Those steps must be done only if you don’t have the DB already installed on your system.*

    ```bash
    sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt/ `lsb_release -cs`-pgdg main" >> /etc/apt/sources.list.d/pgdg.list'
	sudo wget --no-check-certificate --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
	sudo apt update -y; sudo apt install -y postgresql-13 postgresql-13-postgis-3 postgresql-13-postgis-3-scripts postgresql-13 postgresql-client-13
    ```

2.	Create the GeoNode user. GeoNode is going to use this user to access the database

    ```bash
    sudo service postgresql start
	sudo -u postgres createuser -P geonode_odyssey

	# Use this password by default: geonode
    ```

    **NOTE**: *This password is very weak and should be changed.*

3.	Create database `geonode_odyssey` and `geonode_odyssey_data` with owner `geonode_odyssey`

    ```bash
    sudo -u postgres createdb -O geonode_odyssey geonode_odyssey
	sudo -u postgres createdb -O geonode_odyssey geonode_odyssey_data
    ```

 4.	Create PostGIS extensions

    ```bash
    sudo -u postgres psql -d geonode_odyssey -c 'CREATE EXTENSION postgis;'
	sudo -u postgres psql -d geonode_odyssey -c 'GRANT ALL ON geometry_columns TO PUBLIC;'
	sudo -u postgres psql -d geonode_odyssey -c 'GRANT ALL ON spatial_ref_sys TO PUBLIC;'
	sudo -u postgres psql -d geonode_odyssey -c 'GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO geonode_odyssey;'

	sudo -u postgres psql -d geonode_odyssey_data -c 'CREATE EXTENSION postgis;'
	sudo -u postgres psql -d geonode_odyssey_data -c 'GRANT ALL ON geometry_columns TO PUBLIC;'
	sudo -u postgres psql -d geonode_odyssey_data -c 'GRANT ALL ON spatial_ref_sys TO PUBLIC;'
	sudo -u postgres psql -d geonode_odyssey_data -c 'GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO geonode_odyssey;'
    ```
       
5.	Change user access policies for local connections in the file `pg_hba.conf`

    ```bash
    sudo vim /etc/postgresql/13/main/pg_hba.conf
    ```

6.	Make local connection trusted for the default user. Make sure your configuration looks like the one below

    ```bash
    # ...
	# DO NOT DISABLE!
	# If you change this first entry you will need to make sure that the
	# database superuser can access the database using some other method.
	# Noninteractive access to all databases is required during automatic
	# maintenance (custom daily cronjobs, replication, and similar tasks).
	#
	# Database administrative login by Unix domain socket
	local   all             postgres                                trust

	# TYPE  DATABASE        USER            ADDRESS                 METHOD

	# "local" is for Unix domain socket connections only
	local   all             all                                     md5
	# IPv4 local connections:
	host    all             all             127.0.0.1/32            md5
	# IPv6 local connections:
	host    all             all             ::1/128                 md5
	# Allow replication connections from localhost, by a user with the
	# replication privilege.
	local   replication     all                                     peer
	host    replication     all             127.0.0.1/32            md5
	host    replication     all             ::1/128                 md5
    ```

7.	Restart PostgreSQL to make the change effective

    ```bash
    sudo service postgresql restart
    ```

8.	PostgreSQL is now ready. To test the configuration, try to connect to the GeoNode database as GeoNode role

    ```bash
    psql -U postgres geonode_odyssey
	# This should not ask for any password

	psql -U geonode_odyssey geonode_odyssey
	# This should ask for the password geonode

	# Repeat the test with geonode_data DB
	psql -U postgres geonode_odyssey_data
	psql -U geonode_odyssey geonode_odyssey_data
    ```

#### Run GeoNode for the first time in DEBUG Mode

**NOTE**: *This modality is beneficial to debug issues and/or develop new features, but it cannot be used on a production system.*

```bash
# Prepare the GeoNode database (the first time only)
./paver_dev.sh setup
./paver_dev.sh sync
```

**NOTE**: Please verify in the [*views.py*](src/archaeology/views.py) file in the [*archaeology*](src/archaeology) folder, if in the *updateLayers* function the command being executed is *../manage_dev.py* (**If not**, comment out the execution of the command *../manage.py* and uncomment the correct line)

```bash
# Run the server in DEBUG mode
./paver_dev.sh start
```

GeoNode is available at: http://localhost:8000/

**NOTE**: default admin user is ``admin`` (with pw: ``admin``)

GeoServer is available at: http://localhost:8080/geoserver/web/

**NOTE**: default user is ``admin`` (with pw: ``geoserver``)

To stop GeoNode:
```bash
./paver_dev.sh stop
```

### GeoNode-Project Installation with Docker

The installation instructions are based on the [official GeoNode documentation](https://docs.geonode.org/en/3.3.x/install/advanced/project/index.html#deploy-an-instance-of-a-geonode-project-django-template-3-3-2-with-docker-on-localhost) and [GeoNode Training Documentation by GeoSolutions](https://training.geonode.geo-solutions.it/GN3/docker/index.html).

1.	[Docker Setup](https://docs.geonode.org/en/3.3.x/install/advanced/core/index.html#docker) (first time only)

    ```bash
    sudo add-apt-repository universe
	sudo apt-get update -y
	sudo apt-get install -y git-core git-buildpackage debhelper devscripts
	sudo apt-get install -y apt-transport-https ca-certificates curl gnupg-agent software-properties-common

	curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -

	sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"

	sudo apt-get update -y
	sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose
	sudo apt autoremove –purge
    ```

2.	Clone the project from GitHub

    ```bash
    git clone https://github.com/rafaelsa99/odyssey.git
    ```

3.	Create a virtual environment

	```bash
    mkvirtualenv --python=/usr/bin/python3 geonode_odyssey
	workon geonode_odyssey
    ```

4.	Install Django framework

	```bash
    pip install Django==2.2.24
    ```

5.	Build the Docker Containers

**NOTE**: Please verify in the [*views.py*](src/archaeology/views.py) file in the [*archaeology*](src/archaeology) folder, if in the *updateLayers* function the command being executed is *../manage.py* (**If not**, comment out the execution of the command *../manage_dev.py* and uncomment the correct line)
	
	```bash
    cd odyssey/
	docker-compose -f docker-compose.yml build --no-cache
    ```

6.	Run the containers

	```bash
    docker-compose -f docker-compose.yml up -d
    ```

Once the containers are running, GeoNode is available at: http://localhost

**NOTE**: default admin user is ``admin`` (with pw: ``admin``)

GeoServer is available at: http://localhost/geoserver/web/

**NOTE**: default user is ``admin`` (with pw: ``geoserver``)

7.	To stop the containers:

	```bash
	docker-compose -f docker-compose.yml stop
	```

## Deploy on a Domain

**NOTE**: The project is **not** yet ready to deploy to a domain. 

The [official documentation](https://docs.geonode.org/en/3.3.x/install/advanced/project/index.html#deploy-an-instance-of-a-geonode-project-django-template-3-3-2-with-docker-on-a-domain) provides instructions for deploying.

Besides the instructions for deploying, the configurations defined in the .env file must also be changed in a production environment, such as:
- OAUTH2_CLIENT_ID
- OAUTH2_CLIENT_SECRET
- SECRET_KEY (a random one will be generated at project creation)
- DEFAULT_FROM_EMAIL
- Default passwords (e.g., GEOSERVER_ADMIN_PASSWORD, ADMIN_PASSWORD)

## GeoNode Configuration

In addition to the settings presented below, GeoNode allows you to perform other configurations. More information can be found in the [official GeoNode documentation](https://docs.geonode.org/en/3.3.x/index.html).

### Upload Size Limits

By default, GeoNode sets the upload size limit for layers and documents at 100MB. 

To change the upload size limit:
1.	Access Django-Admin http://localhost/admin/
2.	Navigate to Upload → Upload size limits
3.	Change the max size for the layers and documents to the required value (in bytes) (e.g., 10Gb = 10737418240 Bytes)

### Cookies Pop-up

To show the cookies pop-up is necessary to create a GeoNode Theme:
1.	Access Django-Admin http://localhost/admin/
2.	Navigate to GeoNode Themes Library → Themes → Add geo node theme customization
3.	Change the default Body color to #ffffff and the default Navbar color to #101010
4.	Enable the Theme

### Upload INSPIRE Thesaurus

The [official documentation](https://docs.geonode.org/en/3.3.x/admin/thesaurus/index.html) provides instructions for loading thesaurus. 

Adding the INSPIRE Spatial Data Themes thesaurus can be done through the command line or Django Admin.
- Command line with Docker:

	```bash
	cd odyssey/
	workon geonode_odyssey
	docker exec -it django4geonode_odyssey python manage.py load_thesaurus --file inspire-theme.rdf --name inspire_themes
	```

- Command line without Docker:

	```bash
	cd odyssey/src/
	workon geonode_odyssey
	./manage_dev.sh load_thesaurus --file inspire-theme.rdf --name inspire_themes
	```

- From Django Admin:

	1.	Access Django-Admin http://localhost/admin/
	2.	Navigate to Base → Thesauri → Upload thesaurus
	3.	Upload an RDF file

### Upload Layers

Uploading layers can be done via remote services or files.

Some useful layers to add as a Remote Service via WMS:

- [Carta de Uso e Ocupação do Solo – 2018](https://www.dgterritorio.gov.pt/dados-abertos)
	- WMS: https://geo2.dgterritorio.gov.pt/geoserver/COS2018/wms?service=wms&version=1.3.0&request=GetCapabilities
- [Carta Administrativa Oficial de Portugal - CAOP2021 (Continente)](https://www.dgterritorio.gov.pt/dados-abertos)
	- WMS: http://mapas.dgterritorio.pt/wms-inspire/caop/continente?service=WMS&REQUEST=GetCapabilities&VERSION=1.3.0 
- [Carta Geológica de Portugal, na escala 1:500 000](https://geoportal.lneg.pt/pt/dados_abertos/servicos_wms/)
	- WMS: https://sig.lneg.pt/server/services/CGP500k/MapServer/WMSServer

**NOTE:** Information from [DGPC](http://www.patrimoniocultural.gov.pt/pt/recursos/pesquisa-georreferenciada-recursos/) such as the [Archaeology Geoportal](https://patrimoniodgpc.maps.arcgis.com/apps/webappviewer/index.html?id=5cb4735d7d7743a39a16d7269a753a4a%20) is relevant, but it is [published as WFS](https://patrimoniodgpc.maps.arcgis.com/home/item.html?id=b58036247d8849b59b45144135662d86). Thus, it is not possible to upload as a remote service. 

Some layers to upload through files:
- OpenStreetMap Information from Portugal
	- Can be downloaded from https://download.geofabrik.de/europe/portugal-latest-free.shp.zip 

### Add Attributes and Metric Types to the database

The options for Attribute categories and Options and Metric Types can be added manually in Django-Admin. 

Alternatively, they can be entered directly into the database. The following SQL scripts allow you to add a set of predefined options. The attribute information is based on the *Endovélico Thesaurus*.

- With Docker:

	```bash
	cd odyssey/
	workon geonode_odyssey
	docker exec -it db4geonode_odyssey bash
	psql -U postgres geonode_odyssey
	```

- Without Docker:

	```bash
	cd odyssey/src/
	workon geonode_odyssey
	psql -U geonode_odyssey geonode_odyssey
	```

**NOTE:** *For the attribute choices, the script should be changed to insert the corresponding ID of the attribute category added earlier.*

```bash
# For Metric Types:
INSERT INTO metric_type (name) VALUES ('Altura'), ('Comprimento'), ('Largura'), ('Diâmetro'), ('Área');

# For Attribute Categories:
INSERT INTO attribute_category (name) VALUES ('Tipo de sítio'), ('Cronologia'), ('Contexto geológico'), ('Implantação topográfica'), ('Visibilidade'), ('Controlo visual'), ('Uso do solo'), ('Coberto vegetal'), ('Dispersão de materiais (em área)'), ('Tipo de dispersão'), ('Acessibilidade'), ('Trabalhos arqueológicos');

# For Attribute Choices:
#NOTE: for each set of choices you should look at the ID generated for the respective category and replace it in the SQL command.

# For Tipo de sítio:
INSERT INTO attribute_choice (value, category_id) VALUES ('Abrigo', <CAT_TIPO_SITIO_ID>), ('Achado Isolado', <CAT_TIPO_SITIO_ID>), ('Alcaria', <CAT_TIPO_SITIO_ID>), ('Alinhamento', <CAT_TIPO_SITIO_ID>), ('Anfiteatro', <CAT_TIPO_SITIO_ID>), ('Aqueduto', <CAT_TIPO_SITIO_ID>), ('Arte Rupestre', <CAT_TIPO_SITIO_ID>), ('Arranjo de Nascente', <CAT_TIPO_SITIO_ID>), ('Atalaia', <CAT_TIPO_SITIO_ID>), ('Azenha', <CAT_TIPO_SITIO_ID>), ('Balneário', <CAT_TIPO_SITIO_ID>), ('Barragem', <CAT_TIPO_SITIO_ID>), ('Basílica', <CAT_TIPO_SITIO_ID>), ('Calçada', <CAT_TIPO_SITIO_ID>), ('Canalização', <CAT_TIPO_SITIO_ID>), ('Capela', <CAT_TIPO_SITIO_ID>), ('Casal Rústico', <CAT_TIPO_SITIO_ID>), ('Castelo', <CAT_TIPO_SITIO_ID>), ('Cais', <CAT_TIPO_SITIO_ID>), ('Cemitério', <CAT_TIPO_SITIO_ID>), ('Cetária', <CAT_TIPO_SITIO_ID>), ('Chafurdo', <CAT_TIPO_SITIO_ID>), ('Cidade', <CAT_TIPO_SITIO_ID>), ('Circo', <CAT_TIPO_SITIO_ID>), ('Cista', <CAT_TIPO_SITIO_ID>), ('Cisterna', <CAT_TIPO_SITIO_ID>), ('Complexo Industrial', <CAT_TIPO_SITIO_ID>), ('Concheiro', <CAT_TIPO_SITIO_ID>), ('Convento', <CAT_TIPO_SITIO_ID>), ('Criptopórtico', <CAT_TIPO_SITIO_ID>), ('Cromeleque', <CAT_TIPO_SITIO_ID>), ('Curral', <CAT_TIPO_SITIO_ID>), ('Depósito', <CAT_TIPO_SITIO_ID>), ('Edifício com interesse histórico', <CAT_TIPO_SITIO_ID>), ('Eira', <CAT_TIPO_SITIO_ID>), ('Ermida', <CAT_TIPO_SITIO_ID>), ('Escultura', <CAT_TIPO_SITIO_ID>), ('Estrutura com interesse histórico', <CAT_TIPO_SITIO_ID>), ('Fonte', <CAT_TIPO_SITIO_ID>), ('Forja', <CAT_TIPO_SITIO_ID>), ('Forno', <CAT_TIPO_SITIO_ID>), ('Fortificação', <CAT_TIPO_SITIO_ID>), ('Forum', <CAT_TIPO_SITIO_ID>), ('Fossa', <CAT_TIPO_SITIO_ID>), ('Gruta', <CAT_TIPO_SITIO_ID>), ('Hipocausto', <CAT_TIPO_SITIO_ID>), ('Hipódromo', <CAT_TIPO_SITIO_ID>), ('Igreja', <CAT_TIPO_SITIO_ID>), ('Indeterminado', <CAT_TIPO_SITIO_ID>), ('Inscrição', <CAT_TIPO_SITIO_ID>), ('Lagar', <CAT_TIPO_SITIO_ID>), ('Laje Sepulcral', <CAT_TIPO_SITIO_ID>), ('Malaposta', <CAT_TIPO_SITIO_ID>), ('Mancha de Ocupação', <CAT_TIPO_SITIO_ID>), ('Marco', <CAT_TIPO_SITIO_ID>), ('Menir', <CAT_TIPO_SITIO_ID>), ('Mesquita', <CAT_TIPO_SITIO_ID>), ('Miliário', <CAT_TIPO_SITIO_ID>), ('Mina', <CAT_TIPO_SITIO_ID>), ('Moinho de Maré', <CAT_TIPO_SITIO_ID>), ('Moinho de Vento', <CAT_TIPO_SITIO_ID>), ('Monumento Megalítico Funerário', <CAT_TIPO_SITIO_ID>), ('Mosaico', <CAT_TIPO_SITIO_ID>), ('Muralha', <CAT_TIPO_SITIO_ID>), ('Muro', <CAT_TIPO_SITIO_ID>), ('Nicho', <CAT_TIPO_SITIO_ID>), ('Nora', <CAT_TIPO_SITIO_ID>), ('Oficina', <CAT_TIPO_SITIO_ID>), ('Olaria', <CAT_TIPO_SITIO_ID>), ('Palácio', <CAT_TIPO_SITIO_ID>), ('Paço', <CAT_TIPO_SITIO_ID>), ('Pedreira', <CAT_TIPO_SITIO_ID>), ('Pelourinho', <CAT_TIPO_SITIO_ID>), ('Poço', <CAT_TIPO_SITIO_ID>), ('Pombal', <CAT_TIPO_SITIO_ID>), ('Ponte', <CAT_TIPO_SITIO_ID>), ('Povoado', <CAT_TIPO_SITIO_ID>), ('Povoado Fortificado', <CAT_TIPO_SITIO_ID>), ('Recinto', <CAT_TIPO_SITIO_ID>), ('Represa', <CAT_TIPO_SITIO_ID>), ('Salina', <CAT_TIPO_SITIO_ID>), ('Santuário', <CAT_TIPO_SITIO_ID>), ('Sarcófago', <CAT_TIPO_SITIO_ID>), ('Sepultura', <CAT_TIPO_SITIO_ID>), ('Silo', <CAT_TIPO_SITIO_ID>), ('Sinagoga', <CAT_TIPO_SITIO_ID>), ('Talude', <CAT_TIPO_SITIO_ID>), ('Tanque', <CAT_TIPO_SITIO_ID>), ('Teatro', <CAT_TIPO_SITIO_ID>), ('Templo', <CAT_TIPO_SITIO_ID>), ('Termas', <CAT_TIPO_SITIO_ID>), ('Tesouro', <CAT_TIPO_SITIO_ID>), ('Torre', <CAT_TIPO_SITIO_ID>), ('Tulhas', <CAT_TIPO_SITIO_ID>), ('Via', <CAT_TIPO_SITIO_ID>), ('Viaduto', <CAT_TIPO_SITIO_ID>), ('Moinho de Água', <CAT_TIPO_SITIO_ID>), ('Monte', <CAT_TIPO_SITIO_ID>), ('Laje com Covinhas', <CAT_TIPO_SITIO_ID>), ('Pias', <CAT_TIPO_SITIO_ID>), ('Villa', <CAT_TIPO_SITIO_ID>), ('Açude e Dique', <CAT_TIPO_SITIO_ID>), ('Espigueiro', <CAT_TIPO_SITIO_ID>), ('Quinta', <CAT_TIPO_SITIO_ID>), ('Alminha', <CAT_TIPO_SITIO_ID>), ('Cruzeiro', <CAT_TIPO_SITIO_ID>);

# For Cronologia:
INSERT INTO attribute_choice (value, category_id) VALUES ('Paleolítico Inferior', <CAT_CRONOLOGIA_ID>), ('Paleolítico Médio', <CAT_CRONOLOGIA_ID>), (' Paleolítico Superior', <CAT_CRONOLOGIA_ID>), ('Epipaleolítico/Mesolítico', <CAT_CRONOLOGIA_ID>), ('Neolítico', <CAT_CRONOLOGIA_ID>), ('Neolítico Antigo', <CAT_CRONOLOGIA_ID>), ('Neolítico Médio', <CAT_CRONOLOGIA_ID>), ('Neolítico Final', <CAT_CRONOLOGIA_ID>), ('Calcolítico', <CAT_CRONOLOGIA_ID>), ('Calcolítico Final', <CAT_CRONOLOGIA_ID>), ('Bronze Pleno', <CAT_CRONOLOGIA_ID>), ('Bronze Final', <CAT_CRONOLOGIA_ID>), ('Idade do Ferro', <CAT_CRONOLOGIA_ID>), ('1ª Idade do Ferro', <CAT_CRONOLOGIA_ID>), ('2ª Idade do Ferro', <CAT_CRONOLOGIA_ID>), ('Romano', <CAT_CRONOLOGIA_ID>), ('Romano Republicano', <CAT_CRONOLOGIA_ID>), ('Romano Império', <CAT_CRONOLOGIA_ID>), ('Romano Alto Império', <CAT_CRONOLOGIA_ID>), ('Romano Baixo Império', <CAT_CRONOLOGIA_ID>), ('Idade Média', <CAT_CRONOLOGIA_ID>), ('Alta Idade Média', <CAT_CRONOLOGIA_ID>), ('Baixa Idade Média', <CAT_CRONOLOGIA_ID>), ('Islâmico', <CAT_CRONOLOGIA_ID>), ('Moderno', <CAT_CRONOLOGIA_ID>), ('Contemporâneo', <CAT_CRONOLOGIA_ID>), (', Pré-História Antiga', <CAT_CRONOLOGIA_ID>), ('Pré-História Recente', <CAT_CRONOLOGIA_ID>), ('Proto-História', <CAT_CRONOLOGIA_ID>), ('Indeterminado', <CAT_CRONOLOGIA_ID>);

# For Contexto geológico:
INSERT INTO attribute_choice (value, category_id) VALUES ('Granitos', <CAT_CONT_GEO_ID>), ('Xistos', <CAT_CONT_GEO_ID>), ('Calcários', <CAT_CONT_GEO_ID>), ('Aluviões', <CAT_CONT_GEO_ID>), ('Coluviões', <CAT_CONT_GEO_ID>), ('Areias', <CAT_CONT_GEO_ID>), ('Terraço', <CAT_CONT_GEO_ID>), ('Depósitos argilosos', <CAT_CONT_GEO_ID>), ('Rochas vulcânicas', <CAT_CONT_GEO_ID>), ('Dioritos', <CAT_CONT_GEO_ID>), ('Arenitos', <CAT_CONT_GEO_ID>), ('Terraço fluvial/cascalheira', <CAT_CONT_GEO_ID>), ('Outro', <CAT_CONT_GEO_ID>); 

# For Implantação topográfica:
INSERT INTO attribute_choice (value, category_id) VALUES ('Arriba', <CAT_IMP_TOPO_ID>), ('Planície', <CAT_IMP_TOPO_ID>), ('Colina suave', <CAT_IMP_TOPO_ID>), ('Cerro – topo', <CAT_IMP_TOPO_ID>), ('Cerro – vertente', <CAT_IMP_TOPO_ID>), ('Espigão de meandro fluvial', <CAT_IMP_TOPO_ID>), ('Esporão', <CAT_IMP_TOPO_ID>), ('Escarpa', <CAT_IMP_TOPO_ID>), ('Plataforma / rechã', <CAT_IMP_TOPO_ID>), ('Planalto', <CAT_IMP_TOPO_ID>), ('Praia', <CAT_IMP_TOPO_ID>), ('Várzea', <CAT_IMP_TOPO_ID>), ('Leito de rio ou ribeiro', <CAT_IMP_TOPO_ID>);

# For Visibilidade:
INSERT INTO attribute_choice (value, category_id) VALUES ('Destaca-se bem na paisagem', <CAT_VIS_ID>), ('Destaca-se medianamente na paisagem', <CAT_VIS_ID>), ('Diluído na paisagem', <CAT_VIS_ID>), ('Escondido', <CAT_VIS_ID>);

# For Controlo visual:
INSERT INTO attribute_choice (value, category_id) VALUES ('Controlo visual total', <CAT_CONT_VIS_ID>), ('Controlo condicionado', <CAT_CONT_VIS_ID>), ('Controlo restrito (do espaço limítrofe)', <CAT_CONT_VIS_ID>);

# For Uso do solo:
INSERT INTO attribute_choice (value, category_id) VALUES ('Agrícola', <CAT_USO_SOLO_ID>), ('Agrícola regadio', <CAT_USO_SOLO_ID>), ('Baldio', <CAT_USO_SOLO_ID>), ('Florestal', <CAT_USO_SOLO_ID>), ('Industrial', <CAT_USO_SOLO_ID>), ('Pastoreio', <CAT_USO_SOLO_ID>), ('Turismo', <CAT_USO_SOLO_ID>), ('Urbano', <CAT_USO_SOLO_ID>), ('Pedreira', <CAT_USO_SOLO_ID>), ('Areeiro', <CAT_USO_SOLO_ID>), ('Pântano', <CAT_USO_SOLO_ID>), ('Aterro', <CAT_USO_SOLO_ID>), ('Caminho', <CAT_USO_SOLO_ID>);

# For Coberto vegetal:
INSERT INTO attribute_choice (value, category_id) VALUES ('Sem vegetação', <CAT_COB_VEG_ID>), ('Vegetação rasteira', <CAT_COB_VEG_ID>), ('Arbustos ou matos densos', <CAT_COB_VEG_ID>), ('Floresta/mata densa', <CAT_COB_VEG_ID>), ('Floresta/mata pouco densa', <CAT_COB_VEG_ID>), ('Montado', <CAT_COB_VEG_ID>);

# For Dispersão de materiais (em área):
INSERT INTO attribute_choice (value, category_id) VALUES ('Extensa', <CAT_DISP_MAT_ID>), ('Média', <CAT_DISP_MAT_ID>), ('Pequena', <CAT_DISP_MAT_ID>), ('Pontual', <CAT_DISP_MAT_ID>);

# For Tipo de dispersão:
INSERT INTO attribute_choice (value, category_id) VALUES ('Contínua', <CAT_TIPO_DISP_ID>), ('Dispersa', <CAT_TIPO_DISP_ID>), ('Concentrada', <CAT_TIPO_DISP_ID>), ('Progressiva', <CAT_TIPO_DISP_ID>);

# For Acessibilidade:
INSERT INTO attribute_choice (value, category_id) VALUES ('Via Rápida', <CAT_ACE_ID>), ('Estrada Nacional', <CAT_ACE_ID>), ('Estrada Municipal', <CAT_ACE_ID>), ('Estradão', <CAT_ACE_ID>), ('Caminho de pé posto', <CAT_ACE_ID>), ('Sem acesso', <CAT_ACE_ID>);

# For Trabalhos arqueológicos:
INSERT INTO attribute_choice (value, category_id) VALUES ('Conservação/Valorização', <CAT_ARQ_ID>), ('Escavação', <CAT_ARQ_ID>), ('Sondagem', <CAT_ARQ_ID>), ('Levantamento', <CAT_ARQ_ID>), ('Prospecção', <CAT_ARQ_ID>);
```

## GeoServer Configuration

### Create a Data Store

Configure GeoServer to fetch the information from the PostGIS database, based on the information from [GeoServer official documentation](https://geoserver.geo-solutions.it/downloads/releases/2.8.x-ld/doc/gettingstarted/postgis-quickstart/index.html).

1.	In a web browser navigate to: http://localhost/geoserver/web/ 
2.	Navigate to `Data` → `Stores`
3.	Add a `New Data Source` and click in the `PostGIS` link
4.	Enter the following information:
	- Without Docker:
		- Data Source Name: archaeology
		- host: localhost
		- port: 5432
		- database: geonode_odyssey
		- schema: public
		- user: geonode_odyssey
		- passwd: geonode
		- Enable `validate connections` with check box
	- With Docker:
		- Data Source Name: archaeology
		- host: db
		- port: 5432
		- database: geonode_odyssey
		- schema: public
		- user: postgres
		- passwd: postgres
		- Enable `validate connections` with check box
5.	Save

### Create Layers

Create the layers to present the Archaeological Sites and Occurrences added through GeoNode.

1.	In a web browser navigate to http://localhost/geoserver/web/ 
2.	Navigate to `Data` → `Layers`
3.	Add a `New Data Layer`
4.	Choose the `archaeology` Data Store
5.	Click on `Configure new SQL View`

#### Verified Occurrences with points

- View Name: occurrence_point_verified
- SQL statement:

```bash 
select occurrence.id, occurrence.designation, occurrence.acronym, occurrence.toponym, site.name as site_name, occurrence.owner, occurrence.altitude, occurrence.position, people_profile.username as added_by, string_agg(metric_values.automatic_values, ', ') as automatic_metrics, string_agg(metric_values.confirmed_values, ', ') as confirmed_metrics, attributes.values as attributes, 'Verified' as status from occurrence left join (select occurrence_attribute_occurrence.occurrence_id, array_to_string(array_agg(attribute_category.name  || ': ' || attribute_choice.value), ', ') as values from occurrence_attribute_occurrence, attribute_category, attribute_choice where occurrence_attribute_occurrence.attributechoice_id = attribute_choice.id and attribute_choice.category_id = attribute_category.id group by occurrence_attribute_occurrence.occurrence_id) as attributes on attributes.occurrence_id = occurrence.id left join (select metric.occurrence_id, array_to_string(array_agg(metric_type.name || '=' || metric.auto_value || metric.unit_measurement), ', ') as automatic_values, array_to_string(array_agg(metric_type.name  || '=' || metric.confirmed_value || metric.unit_measurement), ', ') as confirmed_values from metric, metric_type where metric.type_id = metric_type.id group by metric.occurrence_id) as metric_values on metric_values.occurrence_id = occurrence.id, people_profile, site where occurrence.added_by_id = people_profile.id and site.id = occurrence.site_id and occurrence.status_occurrence = 'V' group by occurrence.id, attributes.values, people_profile.username, site.name
```

1.	Click on `Refresh`
2.	In the Attributes list, change the *position* to: `Type = Point` and `SRID = 4326`
3.	Click on `Save`
4.	Edit the following information:
	- Title: Verified Archaeological Occurrences [point]
	- Abstract: Verified Occurrences inside the Archaeological Sites represented by points.
	- On Bounding Boxes, click on `Compute from data` and `Compute from native bounds`
5.	Save 

#### Unverified Occurrences with points

- View Name: occurrence_point_unverified
- SQL statement:

```bash 
select occurrence.id, occurrence.designation, occurrence.acronym, occurrence.toponym, site.name as site_name, occurrence.owner, occurrence.altitude, occurrence.position, people_profile.username as added_by, string_agg(metric_values.automatic_values, ', ') as automatic_metrics, string_agg(metric_values.confirmed_values, ', ') as confirmed_metrics, attributes.values as attributes, 'Not Verified' as status from occurrence left join (select occurrence_attribute_occurrence.occurrence_id, array_to_string(array_agg(attribute_category.name  || ': ' || attribute_choice.value), ', ') as values from occurrence_attribute_occurrence, attribute_category, attribute_choice where occurrence_attribute_occurrence.attributechoice_id = attribute_choice.id and attribute_choice.category_id = attribute_category.id group by occurrence_attribute_occurrence.occurrence_id) as attributes on attributes.occurrence_id = occurrence.id left join (select metric.occurrence_id, array_to_string(array_agg(metric_type.name  || '=' || metric.auto_value || metric.unit_measurement), ', ') as automatic_values, array_to_string(array_agg(metric_type.name  || '=' || metric.confirmed_value || metric.unit_measurement), ', ') as confirmed_values from metric, metric_type where metric.type_id = metric_type.id group by metric.occurrence_id) as metric_values on metric_values.occurrence_id = occurrence.id, people_profile, site where occurrence.added_by_id = people_profile.id and site.id = occurrence.site_id and occurrence.status_occurrence = 'N' group by occurrence.id, attributes.values, people_profile.username, site.name
```

1.	Click on `Refresh`
2.	In the Attributes list, change the *position* to: `Type = Point` and `SRID = 4326`
3.	Click on `Save`
4.	Edit the following information:
	- Title: Unverified Archaeological Occurrences [point]
	- Abstract: Unverified Occurrences inside the Archaeological Sites represented by points.
	- On Bounding Boxes, click on `Compute from data` and `Compute from native bounds`
5.	Save 

#### Verified False Positive Occurrences with points

- View Name: occurrence_point_verified_fp
- SQL statement:

```bash 
select occurrence.id, occurrence.designation, occurrence.acronym, occurrence.toponym, site.name as site_name, occurrence.owner, occurrence.altitude, occurrence.position, people_profile.username as added_by, string_agg(metric_values.automatic_values, ', ') as automatic_metrics, string_agg(metric_values.confirmed_values, ', ') as confirmed_metrics, attributes.values as attributes, 'Verified - False Positive' as status from occurrence left join (select occurrence_attribute_occurrence.occurrence_id, array_to_string(array_agg(attribute_category.name  || ': ' || attribute_choice.value), ', ') as values from occurrence_attribute_occurrence, attribute_category, attribute_choice where occurrence_attribute_occurrence.attributechoice_id = attribute_choice.id and attribute_choice.category_id = attribute_category.id group by occurrence_attribute_occurrence.occurrence_id) as attributes on attributes.occurrence_id = occurrence.id left join (select metric.occurrence_id, array_to_string(array_agg(metric_type.name  || '=' || metric.auto_value || metric.unit_measurement), ', ') as automatic_values, array_to_string(array_agg(metric_type.name  || '=' || metric.confirmed_value || metric.unit_measurement), ', ') as confirmed_values from metric, metric_type where metric.type_id = metric_type.id group by metric.occurrence_id) as metric_values on metric_values.occurrence_id = occurrence.id, people_profile, site where occurrence.added_by_id = people_profile.id and site.id = occurrence.site_id and occurrence.status_occurrence = 'F' group by occurrence.id, attributes.values, people_profile.username, site.name
```

1.	Click on `Refresh`
2.	In the Attributes list, change the *position* to: `Type = Point` and `SRID = 4326`
3.	Click on `Save`
4.	Edit the following information:
	- Title: Verified False Positive Archaeological Occurrences [point]
	- Abstract: Verified false positive Occurrences inside the Archaeological Sites represented by points.
	- On Bounding Boxes, click on `Compute from data` and `Compute from native bounds`
5.	Save 

#### Verified True Positive Occurrences with points

- View Name: occurrence_point_verified_tp
- SQL statement:

```bash 
select occurrence.id, occurrence.designation, occurrence.acronym, occurrence.toponym, site.name as site_name, occurrence.owner, occurrence.altitude, occurrence.position, people_profile.username as added_by, string_agg(metric_values.automatic_values, ', ') as automatic_metrics, string_agg(metric_values.confirmed_values, ', ') as confirmed_metrics, attributes.values as attributes, 'Verified - True Positive' as status from occurrence left join (select occurrence_attribute_occurrence.occurrence_id, array_to_string(array_agg(attribute_category.name  || ': ' || attribute_choice.value), ', ') as values from occurrence_attribute_occurrence, attribute_category, attribute_choice where occurrence_attribute_occurrence.attributechoice_id = attribute_choice.id and attribute_choice.category_id = attribute_category.id group by occurrence_attribute_occurrence.occurrence_id) as attributes on attributes.occurrence_id = occurrence.id left join (select metric.occurrence_id, array_to_string(array_agg(metric_type.name  || '=' || metric.auto_value || metric.unit_measurement), ', ') as automatic_values, array_to_string(array_agg(metric_type.name  || '=' || metric.confirmed_value || metric.unit_measurement), ', ') as confirmed_values from metric, metric_type where metric.type_id = metric_type.id group by metric.occurrence_id) as metric_values on metric_values.occurrence_id = occurrence.id, people_profile, site where occurrence.added_by_id = people_profile.id and site.id = occurrence.site_id and occurrence.status_occurrence = 'T' group by occurrence.id, attributes.values, people_profile.username, site.name
```

1.	Click on `Refresh`
2.	In the Attributes list, change the *position* to: `Type = Point` and `SRID = 4326`
3.	Click on `Save`
4.	Edit the following information:
	- Title: Verified True Positive Archaeological Occurrences [point]
	- Abstract: Verified true positive Occurrences inside the Archaeological Sites represented by points.
	- On Bounding Boxes, click on `Compute from data` and `Compute from native bounds`
5.	Save 

#### Verified Sites with points

- View Name: site_point_verified
- SQL statement:

```bash 
select site.id, site.name, site.national_site_code, site.country_iso, site.parish, site.location, people_profile.username as added_by, string_agg(occurrence.designation, ', ') as occurrences, attributes.values as attributes, 'Verified' as status from site left join occurrence on site.id = occurrence.site_id left join (select site_attribute_site.site_id, array_to_string(array_agg(attribute_category.name  || ': ' || attribute_choice.value), ', ') as values from site_attribute_site, attribute_category, attribute_choice where site_attribute_site.attributechoice_id = attribute_choice.id and attribute_choice.category_id = attribute_category.id group by site_attribute_site.site_id) as attributes on attributes.site_id = site.id, people_profile where site.added_by_id = people_profile.id and site.status_site = 'V' group by site.id, attributes.values, people_profile.username
```

1.	Click on `Refresh`
2.	In the Attributes list, change the *location* to: `Type = Point` and `SRID = 4326`
3.	Click on `Save`
4.	Edit the following information:
	- Title: Verified Archaeological Sites [point]
	- Abstract: Verified Archaeological Sites represented by points.
	- On Bounding Boxes, click on `Compute from data` and `Compute from native bounds`
5.	Save 

#### Unverified Sites with points

- View Name: site_point_unverified
- SQL statement:

```bash 
select site.id, site.name, site.national_site_code, site.country_iso, site.parish, site.location, people_profile.username as added_by, string_agg(occurrence.designation, ', ') as occurrences, attributes.values as attributes, 'Not Verified' as status from site left join occurrence on site.id = occurrence.site_id left join (select site_attribute_site.site_id, array_to_string(array_agg(attribute_category.name  || ': ' || attribute_choice.value), ', ') as values from site_attribute_site, attribute_category, attribute_choice where site_attribute_site.attributechoice_id = attribute_choice.id and attribute_choice.category_id = attribute_category.id group by site_attribute_site.site_id) as attributes on attributes.site_id = site.id, people_profile where site.added_by_id = people_profile.id and site.status_site = 'N' group by site.id, attributes.values, people_profile.username
```

1.	Click on `Refresh`
2.	In the Attributes list, change the *location* to: `Type = Point` and `SRID = 4326`
3.	Click on `Save`
4.	Edit the following information:
	- Title: Unverified Archaeological Sites [point]
	- Abstract: Unverified Archaeological Sites represented by points.
	- On Bounding Boxes, click on `Compute from data` and `Compute from native bounds`
5.	Save 

#### Verified Occurrences with polygons

- View Name: occurrence_polygon_verified
- SQL statement:

```bash 
select occurrence.id, occurrence.designation, occurrence.acronym, occurrence.toponym, site.name as site_name, occurrence.owner, occurrence.altitude, occurrence.bounding_polygon, people_profile.username as added_by, string_agg(metric_values.automatic_values, ', ') as automatic_metrics, string_agg(metric_values.confirmed_values, ', ') as confirmed_metrics, attributes.values as attributes, 'Verified' as status from occurrence left join (select occurrence_attribute_occurrence.occurrence_id, array_to_string(array_agg(attribute_category.name  || ': ' || attribute_choice.value), ', ') as values from occurrence_attribute_occurrence, attribute_category, attribute_choice where occurrence_attribute_occurrence.attributechoice_id = attribute_choice.id and attribute_choice.category_id = attribute_category.id group by occurrence_attribute_occurrence.occurrence_id) as attributes on attributes.occurrence_id = occurrence.id left join (select metric.occurrence_id, array_to_string(array_agg(metric_type.name  || '=' || metric.auto_value || metric.unit_measurement), ', ') as automatic_values, array_to_string(array_agg(metric_type.name  || '=' || metric.confirmed_value || metric.unit_measurement), ', ') as confirmed_values from metric, metric_type where metric.type_id = metric_type.id group by metric.occurrence_id) as metric_values on metric_values.occurrence_id = occurrence.id, people_profile, site where occurrence.added_by_id = people_profile.id and site.id = occurrence.site_id and occurrence.status_occurrence = 'V' group by occurrence.id, attributes.values, people_profile.username, site.name
```

1.	Click on `Refresh`
2.	In the Attributes list, change the *bounding_polygon* to: `Type = Polygon` and `SRID = 4326`
3.	Click on `Save`
4.	Edit the following information:
	- Title: Verified Archaeological Occurrences [polygon]
	- Abstract: Verified Occurrences inside the Archaeological Sites represented by polygons.
	- On Bounding Boxes, click on `Compute from data` and `Compute from native bounds`
5.	Save 

#### Unverified Occurrences with polygons

- View Name: occurrence_polygon_unverified
- SQL statement:

```bash 
select occurrence.id, occurrence.designation, occurrence.acronym, occurrence.toponym, site.name as site_name, occurrence.owner, occurrence.altitude, occurrence.bounding_polygon, people_profile.username as added_by, string_agg(metric_values.automatic_values, ', ') as automatic_metrics, string_agg(metric_values.confirmed_values, ', ') as confirmed_metrics, attributes.values as attributes, 'Not Verified' as status from occurrence left join (select occurrence_attribute_occurrence.occurrence_id, array_to_string(array_agg(attribute_category.name  || ': ' || attribute_choice.value), ', ') as values from occurrence_attribute_occurrence, attribute_category, attribute_choice where occurrence_attribute_occurrence.attributechoice_id = attribute_choice.id and attribute_choice.category_id = attribute_category.id group by occurrence_attribute_occurrence.occurrence_id) as attributes on attributes.occurrence_id = occurrence.id left join (select metric.occurrence_id, array_to_string(array_agg(metric_type.name  || '=' || metric.auto_value || metric.unit_measurement), ', ') as automatic_values, array_to_string(array_agg(metric_type.name  || '=' || metric.confirmed_value || metric.unit_measurement), ', ') as confirmed_values from metric, metric_type where metric.type_id = metric_type.id group by metric.occurrence_id) as metric_values on metric_values.occurrence_id = occurrence.id, people_profile, site where occurrence.added_by_id = people_profile.id and site.id = occurrence.site_id and occurrence.status_occurrence = 'N' group by occurrence.id, attributes.values, people_profile.username, site.name
```

1.	Click on `Refresh`
2.	In the Attributes list, change the *bounding_polygon* to: `Type = Polygon` and `SRID = 4326`
3.	Click on `Save`
4.	Edit the following information:
	- Title: Unverified Archaeological Occurrences [polygon]
	- Abstract: Unverified Occurrences inside the Archaeological Sites represented by polygons.
	- On Bounding Boxes, click on `Compute from data` and `Compute from native bounds`
5.	Save 

#### Verified False Positive Occurrences with polygons

- View Name: occurrence_polygon_verified_fp
- SQL statement:

```bash 
select occurrence.id, occurrence.designation, occurrence.acronym, occurrence.toponym, site.name as site_name, occurrence.owner, occurrence.altitude, occurrence.bounding_polygon, people_profile.username as added_by, string_agg(metric_values.automatic_values, ', ') as automatic_metrics, string_agg(metric_values.confirmed_values, ', ') as confirmed_metrics, attributes.values as attributes, 'Verified - False Positive' as status from occurrence left join (select occurrence_attribute_occurrence.occurrence_id, array_to_string(array_agg(attribute_category.name  || ': ' || attribute_choice.value), ', ') as values from occurrence_attribute_occurrence, attribute_category, attribute_choice where occurrence_attribute_occurrence.attributechoice_id = attribute_choice.id and attribute_choice.category_id = attribute_category.id group by occurrence_attribute_occurrence.occurrence_id) as attributes on attributes.occurrence_id = occurrence.id left join (select metric.occurrence_id, array_to_string(array_agg(metric_type.name  || '=' || metric.auto_value || metric.unit_measurement), ', ') as automatic_values, array_to_string(array_agg(metric_type.name  || '=' || metric.confirmed_value || metric.unit_measurement), ', ') as confirmed_values from metric, metric_type where metric.type_id = metric_type.id group by metric.occurrence_id) as metric_values on metric_values.occurrence_id = occurrence.id, people_profile, site where occurrence.added_by_id = people_profile.id and site.id = occurrence.site_id and occurrence.status_occurrence = 'F' group by occurrence.id, attributes.values, people_profile.username, site.name
```

1.	Click on `Refresh`
2.	In the Attributes list, change the *bounding_polygon* to: `Type = Polygon` and `SRID = 4326`
3.	Click on `Save`
4.	Edit the following information:
	- Title: Verified False Positive Archaeological Occurrences [polygon]
	- Abstract: Verified false positive Occurrences inside the Archaeological Sites represented by polygons.
	- On Bounding Boxes, click on `Compute from data` and `Compute from native bounds`
5.	Save 

#### Verified True Positive Occurrences with polygons

- View Name: occurrence_polygon_verified_tp
- SQL statement:

```bash 
select occurrence.id, occurrence.designation, occurrence.acronym, occurrence.toponym, site.name as site_name, occurrence.owner, occurrence.altitude, occurrence.bounding_polygon, people_profile.username as added_by, string_agg(metric_values.automatic_values, ', ') as automatic_metrics, string_agg(metric_values.confirmed_values, ', ') as confirmed_metrics, attributes.values as attributes, 'Verified - True Positive' as status from occurrence left join (select occurrence_attribute_occurrence.occurrence_id, array_to_string(array_agg(attribute_category.name  || ': ' || attribute_choice.value), ', ') as values from occurrence_attribute_occurrence, attribute_category, attribute_choice where occurrence_attribute_occurrence.attributechoice_id = attribute_choice.id and attribute_choice.category_id = attribute_category.id group by occurrence_attribute_occurrence.occurrence_id) as attributes on attributes.occurrence_id = occurrence.id left join (select metric.occurrence_id, array_to_string(array_agg(metric_type.name  || '=' || metric.auto_value || metric.unit_measurement), ', ') as automatic_values, array_to_string(array_agg(metric_type.name  || '=' || metric.confirmed_value || metric.unit_measurement), ', ') as confirmed_values from metric, metric_type where metric.type_id = metric_type.id group by metric.occurrence_id) as metric_values on metric_values.occurrence_id = occurrence.id, people_profile, site where occurrence.added_by_id = people_profile.id and site.id = occurrence.site_id and occurrence.status_occurrence = 'T' group by occurrence.id, attributes.values, people_profile.username, site.name
```

1.	Click on `Refresh`
2.	In the Attributes list, change the *bounding_polygon* to: `Type = Polygon` and `SRID = 4326`
3.	Click on `Save`
4.	Edit the following information:
	- Title: Verified True Positive Archaeological Occurrences [polygon]
	- Abstract: Verified true positive Occurrences inside the Archaeological Sites represented by polygons.
	- On Bounding Boxes, click on `Compute from data` and `Compute from native bounds`
5.	Save 

#### Verified Sites with polygons

- View Name: site_polygon_verified
- SQL statement:

```bash 
select site.id, site.name, site.national_site_code, site.country_iso, site.parish, site.surrounding_polygon, people_profile.username as added_by, string_agg(occurrence.designation, ', ') as occurrences, attributes.values as attributes, 'Verified' as status from site left join occurrence on site.id = occurrence.site_id left join (select site_attribute_site.site_id, array_to_string(array_agg(attribute_category.name  || ': ' || attribute_choice.value), ', ') as values from site_attribute_site, attribute_category, attribute_choice where site_attribute_site.attributechoice_id = attribute_choice.id and attribute_choice.category_id = attribute_category.id group by site_attribute_site.site_id) as attributes on attributes.site_id = site.id, people_profile where site.added_by_id = people_profile.id  and site.status_site = 'V' group by site.id, attributes.values, people_profile.username
```

1.	Click on `Refresh`
2.	In the Attributes list, change the *surrounding_polygon* to: `Type = Polygon` and `SRID = 4326`
3.	Click on `Save`
4.	Edit the following information:
	- Title: Verified Archaeological Sites [polygon]
	- Abstract: Verified Archaeological Sites represented by polygons.
	- On Bounding Boxes, click on `Compute from data` and `Compute from native bounds`
5.	Save 

#### Unverified Sites with polygons

- View Name: site_polygon_unverified
- SQL statement:

```bash 
select site.id, site.name, site.national_site_code, site.country_iso, site.parish, site.surrounding_polygon, people_profile.username as added_by, string_agg(occurrence.designation, ', ') as occurrences, attributes.values as attributes, 'Not Verified' as status from site left join occurrence on site.id = occurrence.site_id left join (select site_attribute_site.site_id, array_to_string(array_agg(attribute_category.name  || ': ' || attribute_choice.value), ', ') as values from site_attribute_site, attribute_category, attribute_choice where site_attribute_site.attributechoice_id = attribute_choice.id and attribute_choice.category_id = attribute_category.id group by site_attribute_site.site_id) as attributes on attributes.site_id = site.id, people_profile where site.added_by_id = people_profile.id  and site.status_site = 'N' group by site.id, attributes.values, people_profile.username
```

1.	Click on `Refresh`
2.	In the Attributes list, change the *surrounding_polygon* to: `Type = Polygon` and `SRID = 4326`
3.	Click on `Save`
4.	Edit the following information:
	- Title: Unverified Archaeological Sites [polygon]
	- Abstract: Unverified Archaeological Sites represented by polygons.
	- On Bounding Boxes, click on `Compute from data` and `Compute from native bounds`
5.	Save

To update GeoNode with the layers created from GeoServer, run:

- With Docker:

	```bash
	cd odyssey/
	workon geonode_odyssey
	docker exec -it django4geonode_odyssey python manage.py updatelayers
	```

- Without Docker:

	```bash
	cd odyssey/src/
	workon geonode_odyssey
	./manage_dev.sh updatelayers
	```

## Some Restrictions to keep in mind when using GeoNode

For the correct operation of some functionalities developed for the project, it is necessary to follow the following restrictions.

### Import Occurrences

Importing occurrences for a given archaeological site only supports CSV files in a predefined format:
- The first line must contain the header, namely "WKT" and "Id".
- The first column, "WKT", must contain the polygon(s) delimiting the occurrences in WKT format. Even if there is only one occurrence, and therefore one polygon, it must be in `MULTIPOLYGON` format. The reference system must be `EPSG:3763 - ETRS89 / Portugal TM06`.
- The second column, "Id", should contain the type of the occurrence(s) of the respective `MULTIPOLYGON`. The type of the occurrence must correspond textually to a Type defined in the GeoNode Attributes.

Example:

```bash
WKT,Id
"MULTIPOLYGON (((-30482.2483797024 252602.781327305,-30466.7142161098 252603.595021589,-30466.9361327325 252587.690996958,-30482.0264630797 252587.764969166,-30482.2483797024 252602.781327305)))","Mamoa"
"MULTIPOLYGON (((-30052.7657424689 239969.067994009,-30034.2726905728 239970.325521538,-30033.9028295349 239951.314664189,-30052.6917702613 239952.720136133,-30052.7657424689 239969.067994009)))","Abrigo"
```

### Automatic Identification

The automatic identification of occurrences using the algorithm has some restrictions to be considered:
- Only occurrences with a defined polygon are fed into the algorithm. Occurrences defined only by a point are not used, because they do not geographically define the limits of the occurrence.
- Only occurrences with a type assigned and the Status *Verified* or *Verified - True Positive* are considered. *Unverified* or *false positive* occurrences are not considered for the execution of the algorithm.
- Only `GeoTIFF` layers can be chosen to run the algorithm. The format of the layer names must be consistent for correct identification by the algorithm. The name must have the format `name_type.tif` (e.g., `laboreiro_lrm.tif`).
- The area of interest for the algorithm's execution must intersect at least one layer and one occurrence. Furthermore, and considering the size of the layers that must be fed into the algorithm, the size of the area of interest should not be excessively large. The selection of an area of interest of reasonable size is left to the user.
- For a correct identification of the type of occurrence that has been identified, the name of the attribute category for the occurrence type should be "Type" or "Tipo".

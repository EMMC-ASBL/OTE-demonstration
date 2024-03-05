# Introduction

This repository demonstrates how to use the core component of the Open Translation Environment (OTE) developed during the [OntoTrans project](https://cordis.europa.eu/project/id/862136). The aim of this demonstration is to semantically describe different datasets by using a domain ontology based on EMMO (1.0.0-beta7) and to store the ontological mapping, distribution address, and other metadata in a Knowledge Base (KB) for later retrieval. The datasets in this demonstration are output files from  Molecular Dynamics (MD) simulations and experimental data organised in a spreadsheet. They are example of unstructured data whose meaning is well known to the scientists who produced them, but not to third-party users. The process of documenting and storing data semantically using the OTE is a practical example of creating FAIR data which meet the principles of Findability, Accessibility, Interoperability, and Reusability.

The OTE software components can be installed locally with the Python pip package manager. Alternatively, a VirtualBox image of a Linux OS with the pre-installed components is available for [download](https://drive.google.com/file/d/1MsjibdPLPhd1DdfXvMCy6F2-4LaUeNG3/view?usp=drive_link). Bear in mind that the image is 3.29 GB and it will occupy roughly 10 GB when executed.

### MD simulations

The following simulations were executed with a [modified version of LAMMPS](https://github.com/sfarr-epcc/lammps_MOLC) implementing the MOLC model.
* For the coarse-grained model:
  ```bash
  moltemplate.sh -atomstyle "hybrid molecular ellipsoid" -dump benzene_00.dump benzene_01.lt ; rm -fr output_ttree/
  nohup mpirun -np 4 lmp_2Jun22 -in benzene_01.in -l benzene_01.log &
  ```
* Conversion from CG to AA coordinates:
  ```bash
  dumptools -w -f last -o benzene_01.last benzene_01.dump
  backmap_legacy -t /usr/local/share/forcefields/molc/benzene/t1_benzene.xyz -o benzene_aa benzene_01.last.dump
  ```
* For the atomistic model:
  ```bash
  moltemplate.sh -overlay-all -pdb ../cg/benzene_aa.00100000 benzene_01.lt
  data2psf -d 258 benzene_aa.pdb benzene_01.data
  nohup mpirun -np 4 lmp_2Jun22 -in benzene_01.in -l benzene_01.log &
  ```

### Experimental data

The folder [experimental](./experimental) contains a spreadsheet with liquid-phase properties of water, benzene, and hexane solvents, taken from the NIST TDE database.

# 1. Ontology Development

The ontology is created using an empty template file in turtle format (TTL). Classes are added describing the dataset, its components, and their relationships. The ontology editor Protégé is used to develop the ontology. To speed up the import of EMMO modules, a link to the application ontology is created in the EMMO repository, as to access the modules locally.

1. Let's start by defining the class Solvent in terms of EMMO classes:
   hasHolisticPart (IRI: `EMMO_8e52c42b_e879_4473_9fa1_4b23428b392b`)
   Solution (IRI: `EMMO_2031516a_2be7_48e8_9af7_7e1270e308fe`).
   To import the EMMO modules containing these concepts, search for the IRIs in the EMMO repository, e.g. by

   ```bash
   find . -name "*ttl" -exec grep -l EMMO_2031516a_2be7_48e8_9af7_7e1270e308fe '{}' \;
   ./perspectives/physicalistic.ttl
   ```

   Which means that the the following import is needed:
   ```turtle
   owl:imports <http://emmo.info/emmo/1.0.0-beta5/perspectives/physicalistic> ;
   ```

2. Benzene is a Solvent, but also a subclass of Liquid.

3. The `ISQ` module provides the definition of many physical observables. The speed of sound is not among the ones already defined, so a new subclass must be created under the `Speed` class.

4. A class describing the experimental dataset is created, which contains all the physical observables, plus a reference to the material(s) they refer to.

5. The quantities in the molecular modelling simulations need first to be defined, before referring them in the dataset.

# 2. Data and Metadata Mapping

[DLite data models](https://sintef.github.io/dlite/getting_started/tutorial.html) are files in the [JSON format](https://attacomsian.com/blog/what-is-json) that are used to describe the structure of the input datasets.

The table below summarises the different data types defined in DLite.

| type      | datatype       | sizes                  | description                      | examples                                                     |
| --------- | -------------- | ---------------------- | -------------------------------- | ------------------------------------------------------------ |
| blob      | dliteBlob      | any                    | binary blob, sequence of bytes   | blob32, blob128, …                                           |
| bool      | dliteBool      | sizeof(bool)           | boolean                          | bool                                                         |
| int       | dliteInt       | 1, 2, 4, {8}           | signed integer                   | (int), int8, int16, int32, {int64}                           |
| uint      | dliteUInt      | 1, 2, 4, {8}           | unsigned integer                 | (uint), uint8, uint16, uint32, {uint64}                      |
| float     | dliteFloat     | 4, 8, {10, 12, 16}     | floating point                   | (float), (double), float32, float64, {float80, float96, float128} |
| fixstring | dliteFixString | any                    | fix-sized NUL-terminated string  | string20, string4000, …                                      |
| ref       | dliteRef       | sizeof(DLiteInstance*) | reference to another instance    | ref, http://onto-ns.com/meta/0.1/MyEntity                    |
| string    | dliteStringPtr | sizeof(char *)         | pointer to NUL-terminated string | string                                                       |
| relation  | dliteRelation  | sizeof(DLiteRelation)  | subject-predicate-object triplet | relation                                                     |
| dimension | dliteDimension | sizeof(DLiteDimension) | only intended for metadata       | dimension                                                    |
| property  | dliteProperty  | sizeof(DLiteProperty)  | only intended for metadata       | property                                                     |

**Metadata**

For all: access URL.

For the experimental data: reference.

For the simulations is the input deck for LAMMPS, containing:

* timestep
* units
* materials model (eg the force field)


# 3. OntoREC and GraphDB Deployment
To run OntoREC and GraphDB component you need a proper installation of Docker and Docker Compose.
The following steps contains some details specific for the installation of Docker on the Sparky distribution, for a more general apporach please refer to the official [Docker guide](https://docs.docker.com/engine/install/debian/).

```bash
# Add Docker's official GPG key:
sudo apt-get update
sudo apt-get install ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# Add the repository to Apt sources:
echo \
  "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian \
  "$(. /etc/os-release && echo "bookworm")" stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update

sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin docker-compose

```

Once Docker is installed and properly running, clone the repository related to the OntoREC component and use the branch for the graphdb deployment:

```bash
git clone git@gitlab.cc-asp.fraunhofer.de:ontotrans/ontotranscorecomponents.git
git checkout test/graphdb-backend
```

Now run the service in the docker-compose_graphdb_dev.yml file:

```bash
sudo docker login  registry.gitlab.cc-asp.fraunhofer.de
sudo docker-compose -f docker-compose_graphdb_dev.yml up -d
```

All service should be up and running.

# [WIP]HakuBooru - text-image dataset maker for booru style image platform

**This repo is still WIP**

## Introduction

**Project Overview**

This project introduces a robust dataset exporter specifically designed for online image platforms, particularly those in the booru series.

We addresses a critical issue prevalent in dataset creation - the excessive use of crawlers. As user numbers swell, these crawlers often lead to unintentional "bot spam" or can even escalate to forms of DDoS attacks.

To mitigate these issues, our approach leverages pre-downloaded or previously dumped data to construct datasets, significantly reducing the impact on the original websites.

**Key Features**

The framework integrates several functionalities, streamlining the creation of custom datasets:

* **Metadata-Based Image Selection**
  * Simulates the "search by tag" functionality found in typical booru websites.
  * Offers options to filter explicit images or, conversely, to select only explicit content.
  * Excludes low-scoring images, among other customizable filters.
  * etc.
* **Image Captioning**
  * Utilizes metadata from xxxbooru-like platforms for generating quality and year tags.

You are also encouraged to develop and integrate your own components to enhance or replace existing stages of this framework. We warmly welcome contributions in the form of pull requests for new built-in processors as well!

The combination of these features not only preserves the integrity of source platforms but also offers users an efficient and customizable tool for dataset creation.

~~Thx ChatGPT4 for this introduction :p~~

## Resources

* [danbooru2023-sqlite](https://huggingface.co/datasets/KBlueLeaf/danbooru2023-sqlite)
* [danbooru2023-webp-2Mpixel](https://huggingface.co/datasets/KBlueLeaf/danbooru2023-webp-2Mpixel)

## Setup

You can install this package through PyPi with pip utilities:

```bash
python -m pip install hakubooru
```

Or build from source:

```bash
git clone https://github.com/KohakuBlueleaf/HakuBooru
cd HakuBooru
python -m pip install -e .
```

## Components

This project have quite simple workflow to export the images from tarfiles into folders.

And the whole workflow is composed by following components:

* Post chooser
* Captioner
* Saver
* Exporter

The Exporter is for reading the tarfile, picking choosed post (a list of posts generated by the post chooser), sending them into captioner and saver. Normally you don't need to modify the workflow of Exporter (Unless you want to utilize your own data source or add more pre/post processing to the image/caption)

The captioner is for generating the caption of the image based on its own data(the image) or its metadata (the KohakuCaptioner used in example).

The saver is for saving the target data (with id, img bytes, caption text) into disk. We have 2built-in saver:

* File saver: which will save image and caption into seperated files with same id (same basename)
* WDS saver: will save datas into tar file with webdataset format.

## Usage

Based on the components we have, it is clear that how should we do to utilize this project.

At first you need to download the metadata database from [here](https://huggingface.co/datasets/KBlueLeaf/danbooru2023-sqlite/blob/main/danbooru2023.db) and download the danbooru tarfiles from [here](https://huggingface.co/datasets/KBlueLeaf/danbooru2023-webp-2Mpixel). Put the database file into `DB.db` and image tar files into `IMAGE_FOLDER/data-xxxx.tar`. (`DB` and `IMAGE_FOLDER` can be any path you want, remember them, we will use them later)

And now we start using this library:

```python
import logging

from hakubooru.dataset import load_db, Post
from hakubooru.dataset.utils import (
    get_post_by_tags,
    get_tag_by_name,
)
from hakubooru.caption import KohakuCaptioner
from hakubooru.export import Exporter, FileSaver
from hakubooru.logging import logger


if __name__ == "__main__":
    logger.setLevel(logging.INFO)
    logger.info("Loading database")
    load_db("DB")
```

^ At first we import all the needed library and load the database file. (replace `DB` with your db file path)

And then select the posts we want to export:

```python
    logger.info("Querying posts")
    # Querying posts for:
    # * whose tag_list have any of the following tags:
    #   * rice_shower_(umamusume)
    #   * mejiro_mcqueen_(umamusume)
    # * whose rating < 3 (avoid explicit images)
    # * whose score > 10 (better preference)
    choosed_post = list(
        get_post_by_tags(
            [
                get_tag_by_name(tag)
                for tag in [
                    "rice_shower_(umamusume)",
                    "mejiro_mcqueen_(umamusume)",
                ]
            ]
        ).where(Post.rating < 2, Post.score > 10)
    )
    logger.info(f"Found {len(choosed_post)} posts")
```

^ The "Post" object is a peewee model, you can refer to these documentations for how to utlize Peewee ORM to query the posts. And definitely, you can use some simple query and then filter them in plain python.

Now we have choosed posts we want to export, the last thing is to make an exporter and run it:

```python
    logger.info("Build exporter")
    exporter = Exporter(
        dataset_dir="IMAGE_FOLDER",
        saver=FileSaver("./out/example"),
        captioner=KohakuCaptioner(),
    )
    logger.info("Exporting images")
    exporter.export_posts(choosed_post)
```

^ This code build an exporter which take tar files from `IMAGE_FOLDER` with:

* saver: FileSaver which output folder is `./out/example`
* captioner: KohakuCaptioner with all default settings.

This example code will do:

* Choosing post with `rice_shower_(umamusume)` and `mejiro_mcqueen_(umamusume)` tag in it.
  * Also with rating = general/sensitive and score>10. (score = up votes - down votes)
* Reading image from `IMAGE_FOLDER/data-xxxx.tar`
* Send image and metadata into `KohakuCaptioner()`
* Use `FileSaver("./out/example")` to save the image and caption.

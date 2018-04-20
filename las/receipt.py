from ._document import Document


class Receipt(Document):
    """a Receipt object contains image or pdf data of a receipt and is
    typically passed to :py:class:`~las.client.Client` for scanning.
    Supported file formats are jpeg, png, gif, bmp and pdf.

    :param str url: An http or https url pointing to an receipt image or pdf.
    :param str filename: A path to a local receipt image or pdf file.
    :param typing.BinaryIO fp: A file-like python object
    :param bytes content: Binary receipt image or pdf data.

    """

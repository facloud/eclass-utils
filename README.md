# UoA E-Class utilities

## scrap-dir.py

Useful to download contents of a given directory in E-class. Say we want to
scrap root directory of course `DI352`:

```bash
$ ./scrap-dir.py -c DI352
Username: sdi0800073
Password: *******
[INFO] Downloading 3 URLs...
[INFO] Downloading: ./Sample Datasets (εργασία 1).zip Bytes: 1382457
    1382457  [100.00%]
[INFO] Downloading: ./Διαφάνειες.zip Bytes: 1954080
    1954080  [100.00%]
[INFO] Downloading: ./Εργασίες.zip Bytes: 169930
     169930  [100.00%]
```

Maybe this is too much, let's just download the lecture PDFs. If find that the
directory that holds this PDFs can be browsed from this location:
`http://eclass.uoa.gr/modules/document/document.php?course=DI352&openDir=/5432bb8emlOA`.
Use the `openDir` argument (`/5432bb8emlOA`) as follows:

```bash
$ ./scrap-dir.py -c DI352 -r /5432bb8emlOA
Username: sdi0800073
Password: *******
[INFO] Downloading 5 URLs...
[INFO] Downloading: ./0.eisagwgh.pdf Bytes: 314294
     314294  [100.00%]
[INFO] Downloading: ./0b.program_organization&design.pdf Bytes: 683521
     683521  [100.00%]
[INFO] Downloading: ./1.nnLSH.pdf Bytes: 288610
     288610  [100.00%]
[INFO] Downloading: ./1b.PseudoRandom&Hashtable.pdf Bytes: 145949
     145949  [100.00%]
[INFO] Downloading: ./2.cluster.pdf Bytes: 1110465
    1110465  [100.00%]
```

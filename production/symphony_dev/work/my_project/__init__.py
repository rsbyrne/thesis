################################################################################



import symphony


def get_params(project, /):
    for item in (
            'foo', 'bah', 'qux', 'zap', 'vim', 'lop', 'dab', 'wam',
            'tig', 'pek', 'yap', 'jot', 'rum', 'sod', 'kik',
            ):
        yield item


def run(job, /):

    with (job.outdir / 'data.txt').open('w') as file:
        file.write(job.params * 3)



################################################################################
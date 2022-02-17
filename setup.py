from setuptools import setup, find_packages 

setup(
    name='do-not-be-fooled-tw', 
    version='0.1', 
    install_requires=[
        'openpyxl', 
        'pandas', 
        'scrapy', 
        'click', 
        'validators'
    ], 
    packages=find_packages('src'), 
    package_dir={
        'do_not_be_fooled_tw': 'src/do_not_be_fooled_tw'
    }, 
    description='Do not be fooled! Taiwanese!', 
    author='Wei-Fan Chiang', 
    license='BSD', 
    zip_safe=True, 
    python_requires='>=3.7'
)
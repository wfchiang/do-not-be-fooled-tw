from setuptools import setup, find_packages 

setup(
    name='do-not-be-fooled-tw', 
    version='0.1.0', 
    install_requires=[
        'regex', 
        'openpyxl', 
        'pandas', 
        'scrapy', 
        'click', 
        'validators'
    ], 
    include_package_data = True, 
    packages=find_packages('src'), 
    package_dir={
        '': 'src'
    }, 
    description='Do not be fooled! Taiwanese!', 
    author='Wei-Fan Chiang', 
    license='BSD', 
    zip_safe=True, 
    python_requires='>=3.7'
)
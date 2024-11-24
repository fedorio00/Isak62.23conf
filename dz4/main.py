import click
from assembler import Assembler
from interpreter import VirtualMachine

@click.group()
def cli():
    """Учебная виртуальная машина (УВМ)"""
    pass

@cli.command()
@click.argument('source', type=click.Path(exists=True))
@click.argument('output', type=click.Path())
@click.argument('log', type=click.Path())
def assemble(source: str, output: str, log: str):
    """Ассемблирует исходный код в бинарный файл."""
    assembler = Assembler()
    try:
        assembler.assemble(source, output, log)
        click.echo(f"Программа успешно ассемблирована в {output}")
        click.echo(f"Лог сохранен в {log}")
    except Exception as e:
        click.echo(f"Ошибка при ассемблировании: {str(e)}", err=True)
        raise click.Abort()

@cli.command()
@click.argument('binary', type=click.Path(exists=True))
@click.argument('output', type=click.Path())
@click.option('--memory-range', '-m', type=str, required=True,
              help='Диапазон памяти для вывода (start-end)')
def run(binary: str, output: str, memory_range: str):
    """Выполняет бинарный файл на виртуальной машине."""
    try:
        start, end = map(int, memory_range.split('-'))
    except ValueError:
        click.echo("Неверный формат диапазона памяти. Используйте формат: start-end", err=True)
        raise click.Abort()

    vm = VirtualMachine()
    try:
        with open(binary, 'rb') as f:
            program = f.read()
        
        vm.load_program(program)
        vm.run()
        vm.dump_memory(start, end, output)
        
        click.echo(f"Программа успешно выполнена")
        click.echo(f"Результат сохранен в {output}")
    except Exception as e:
        click.echo(f"Ошибка при выполнении: {str(e)}", err=True)
        raise click.Abort()

if __name__ == '__main__':
    cli()

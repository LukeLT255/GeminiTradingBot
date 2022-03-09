import C3PO
import cronitor
import config

cronitor.api_key = config.cron_key


@cronitor.job("Ev6pqq")
def runC3PO():
    C3PO.make_dem_trades()


if __name__ == '__main__':
    runC3PO()

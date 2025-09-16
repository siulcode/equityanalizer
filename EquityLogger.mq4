//+------------------------------------------------------------------+
//| Equity Logger EA - Logs equity every second                      |
//+------------------------------------------------------------------+
#property strict

input bool SaveToFile = true;         // Enable CSV logging
input string FileName = "EquityLog.csv"; // CSV file name

datetime lastLoggedTime = 0;

int OnInit()
{
   Print("Equity Logger EA initialized.");
   return INIT_SUCCEEDED;
}

void OnTick()
{
   datetime currentTime = TimeCurrent();

   // Log once per second
   if (currentTime != lastLoggedTime)
   {
      double equity = AccountEquity();
      string timestamp = TimeToString(currentTime, TIME_DATE | TIME_SECONDS);
      string logLine = timestamp + " | Equity: " + DoubleToString(equity, 2);

      Print(logLine); // Log to Experts tab

      if (SaveToFile)
      {
         int fileHandle = FileOpen(FileName, FILE_CSV | FILE_WRITE | FILE_READ | FILE_ANSI);
         if (fileHandle != INVALID_HANDLE)
         {
            FileSeek(fileHandle, 0, SEEK_END);
            FileWrite(fileHandle, timestamp, equity);
            FileClose(fileHandle);
         }
         else
         {
            Print("Error opening file: ", FileName);
         }
      }

      lastLoggedTime = currentTime;
   }
}
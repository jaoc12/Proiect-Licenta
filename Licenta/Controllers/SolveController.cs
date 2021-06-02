using Licenta.Models;
using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Web;
using System.Web.Mvc;

namespace Licenta.Controllers
{
    public class SolveController : Controller
    {
        // GET: Solve
        public ActionResult Index()
        {
            return View();
        }

        [HttpGet]
        public ActionResult Detection()
        {
            String jsonName = "sudoku.json";
            String pathToImages = Server.MapPath("~/Python/Date/Sudoku/");

            String pathToJson = (pathToImages + jsonName);
            String json = System.IO.File.ReadAllText(pathToJson);
            Sudoku sudoku = JsonConvert.DeserializeObject<Sudoku>(json);

            return View(sudoku);
        }

        [HttpPut]
        public ActionResult Solution(Sudoku sudoku)
        {
            string json = JsonConvert.SerializeObject(sudoku);
            string path = Server.MapPath("~/Python/Date/Json/sudoku_de_rezolvat.json");
            System.IO.File.WriteAllText(path, json);

            RunSolver();

            String nameSolved = "sudoku_rezolvat.json";
            String pathSolved = Server.MapPath("~/Python/Date/Json/");

            String pathToJson = (pathSolved + nameSolved);
            String jsonSolved= System.IO.File.ReadAllText(pathToJson);
            Sudoku sudokuSolved = JsonConvert.DeserializeObject<Sudoku>(jsonSolved);

            sudokuSolved.Original = new List<bool>();
            for(int i=0; i<81; i++)
            {
                if(sudoku.Grid[i] != 0)
                {
                    sudokuSolved.Original.Add(true);
                }
                else
                {
                    sudokuSolved.Original.Add(false);
                }
            }

            return View(sudokuSolved);
        }

        [NonAction]
        private void RunSolver()
        {
            string path = Server.MapPath("~/Python/Cod/solver.bat");
            Process process = new Process();
            process.StartInfo.FileName = path;
            process.StartInfo.UseShellExecute = false;
            process.StartInfo.WorkingDirectory = Server.MapPath("~/Python/Cod/");
            process.Start();
            process.WaitForExit();
        }
    }
}
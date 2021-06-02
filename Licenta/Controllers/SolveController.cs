using Licenta.Models;
using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Net;
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
            if(ValidateGrid(sudoku) == false)
            {
                return new HttpStatusCodeResult(HttpStatusCode.BadRequest, "bad sudoku input");
            }

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
        private bool ValidateGrid(Sudoku sudoku)
        {
            // verifica daca sunt doar cifre de la 0 la 9
            for (int i = 0; i < 81; i++)
            {
                if (sudoku.Grid[i] < 0 || sudoku.Grid[i] > 9)
                {
                    return false;
                }
            }

            // verifica daca fiecare linie/coloana este corect
            for(int i=0; i < 9; i++)
            {
                for(int j = 0; j < 9; j++)
                {
                    for(int k=0; k < 9; k++)
                    {
                        if(sudoku.Grid[i*9 + j] == sudoku.Grid[i*9 + k] && j != k)
                        {
                            return false;
                        }
                        if(sudoku.Grid[i + j*9] == sudoku.Grid[i + k*9] && j != k)
                        {
                            return false;
                        }
                    }
                }
            }

            // verifica daca fiecare patrat este corect
            for(int i_square=0; i_square < 3; i_square++)
            {
                for(int j_square = 0; j_square < 3; j_square++)
                {
                    for(int i=0; i < 9; i++)
                    {
                        for(int j=0; j<9; j++)
                        {
                            int iCell1 = i_square * 3 + i / 3;
                            int jCell1 = j_square * 3 + i % 3;
                            int iCell2 = i_square * 3 + j / 3;
                            int jCell2 = j_square * 3 + j % 3;
                            if(i != j && sudoku.Grid[iCell1*9 + jCell1] == sudoku.Grid[iCell2*9 + jCell2])
                            {
                                return false;
                            }
                        }
                    }
                }
            }

            return true;
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
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
    public class ImageController : Controller
    {
        // GET: Image
        public ActionResult Index()
        {
            return View();
        }

        [HttpPost]
        public ActionResult New(HttpPostedFileBase upload)
        {
            if(upload != null && upload.ContentLength > 0)
            {
                String fileName = "sudoku.jpg";
                String pathToImages = Server.MapPath("~/Python/Date/Sudoku/");
                upload.SaveAs(pathToImages + fileName);

                RunDetector();
                RunClasificator();

                return RedirectToAction("Detection", "Solve");
            }
            return RedirectToAction("Index", "Solve");
        }

        [NonAction]
        private void RunDetector()
        {
            string path = Server.MapPath("~/Python/Cod/detector.bat");
            Process process = new Process();
            process.StartInfo.FileName = path;
            process.StartInfo.UseShellExecute = false;
            process.StartInfo.WorkingDirectory = Server.MapPath("~/Python/Cod/");
            process.Start();
            process.WaitForExit();
        }

        [NonAction]
        private void RunClasificator()
        {
            string path = Server.MapPath("~/Python/Cod/clasificator.bat");
            Process process = new Process();
            process.StartInfo.FileName = path;
            process.StartInfo.UseShellExecute = false;
            process.StartInfo.WorkingDirectory = Server.MapPath("~/Python/Cod/");
            process.Start();
            process.WaitForExit();
        }
    }
}
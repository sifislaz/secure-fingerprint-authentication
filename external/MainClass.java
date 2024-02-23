package minutiaeextraction;

import java.util.Base64;
import java.nio.file.Files;
import java.nio.file.Path;

import com.machinezoo.sourceafis.*;

public class MainClass {

	public static void main(String[] args) {
		Path path = Path.of(args[0]);
		Double dpi = Double.parseDouble(args[1]);
//		System.out.println(path);
		try {
			byte[] encodedImg = Files.readAllBytes(path);
			FingerprintImageOptions opt = new FingerprintImageOptions().dpi(dpi);
			FingerprintImage img = new FingerprintImage(encodedImg, opt);
			FingerprintTemplate temp = new FingerprintTemplate(img);
			String b64temp = Base64.getEncoder().encodeToString(temp.toByteArray());
			System.out.println(b64temp);
		
		}
		catch(Exception e) {
			e.printStackTrace();
			
		}
		
	}

}
